import json
from timeit import default_timer as timer

from etl import etl_func


def get_steps(file=None):
    if file is None:
        file = "db/cassandra/udf/pushdown.json"
    with open(file) as f:
        pushdown = json.load(f)

    return pushdown


def process_steps(udf: dict, ses):
    dataframes = dict()

    for step in udf['steps']:
        step_time_info = {
            "data_acquisition_time": [],
            "data_processing_time": [],
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
                sti_tb = {"table": tb_name, "time": -1}
                sti_pt = {"table": tb_name, "time": -1}

                query = udf['datasets'][tb_name]['query']
                dat_1 = timer()
                df = ses.execute(query, timeout=None)._current_rows
                dat_2 = timer()
                sti_tb['time'] = dat_2 - dat_1

                if 'index' in udf['datasets'][tb_name]:
                    df.set_index(udf['datasets'][tb_name]['index'])
                dataframes[tb_name] = df
                dat_3 = timer()
                sti_pt['time'] = dat_3 - dat_2

                sti['data_acquisition_time'].append(sti_tb)
                sti['data_processing_time'].append(sti_pt)
            args[args_key] = dataframes[tb_name]

        if 'args' in step:
            args.update(step['args'])
        spt_1 = timer()
        func = etl_func.func_map[step["etl_func"]]
        spt_2 = timer()
        sti['etl_processing_time'] = spt_2 - spt_1
        dataframes[step['output']] = func(**args)
        if "remove" in step:
            for rm_db in step["remove"]:
                dataframes.pop(rm_db, None)
        time_end = timer()
        sti['overall_time'] = time_end - time_start
        step['time_info'] = sti

    return udf










