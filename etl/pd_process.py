import json
from timeit import default_timer as timer

from cassandra.cluster import Cluster, Session
from cassandra.cluster import ResultSet
from cassandra.query import SimpleStatement
import pandas as pd
from etl import etl_func


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def get_steps(file=None):
    if file is None:
        print("File is None")
        exit(-1)
    with open(file) as f:
        pushdown = json.load(f)

    return pushdown


def process_steps(udf: dict, cluster):


    dataframes = dict()

    for step in udf['steps']:
        step_time_info = {
            "data_acquisition_time": [],
            "etl_processing_time": -1.,
            "overall_time": -1.
        }
        time_start = timer()

        args_tb = step["args_tb"]
        args = dict()
        sti = step_time_info.copy()


        for args_key in args_tb.keys():


            tb_name = args_tb[args_key]
            if tb_name not in dataframes:
                sti_tb = {"table": tb_name, "time": -1, "rows": -1}

                query = udf['datasets'][tb_name]['query']
                statement = SimpleStatement(query, fetch_size=5000)
                dat_1 = timer()

                session: Session = cluster.connect()
                session.row_factory = pandas_factory

                ex: ResultSet = session.execute(statement, timeout=120)
                df = ex._current_rows
                while ex.has_more_pages:
                    ex.fetch_next_page()
                    df = df.append(ex._current_rows)

                session.shutdown()

                dat_2 = timer()

                dataframes[tb_name] = df

                sti_tb['time'] = dat_2 - dat_1
                print(f"Rows: {len(df.index)} for {tb_name}")
                sti['data_acquisition_time'].append(sti_tb)

            args[args_key] = dataframes[tb_name]

        if 'args' in step:
            args.update(step['args'])

        func = etl_func.func_map[step["etl_func"]]

        spt_1 = timer()
        res = func(**args)
        dataframes[step['output']] = res
        spt_2 = timer()

        sti['etl_processing_time'] = spt_2 - spt_1
        if "remove" in step:
            for rm_db in step["remove"]:
                dataframes.pop(rm_db, None)
        time_end = timer()
        sti['overall_time'] = time_end - time_start
        step['time_info'] = sti

    return udf
