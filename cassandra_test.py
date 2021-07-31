import io
from datetime import  datetime

import yaml
from cassandra.cluster import Cluster
import json

from pyspark.sql import SparkSession

from grid import create_scenarios
from etl.etl_setup import select_driver


import logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
print = rootLogger.info

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

fileHandler = logging.FileHandler(f"run_{datetime.now().strftime('%Y%m%d')}.result.log", mode='a')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)


def write_to(file_name, data, output_path=None, mode='w'):
    if output_path is not None:
        file_name = f"{output_path}/{file_name}"
    with open(file_name, mode) as cmd_file:
        cmd_file.write(data)


def write_to_yaml(file_name, data, output_path=None, mode='a'):
    if output_path is not None:
        file_name = f"{output_path}/{file_name}"
    with io.open(file_name, mode, encoding='utf8') as outfile:
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)


def load_from_json(file_name, path=None):
    if path is not None:
        file_name = f"{path}/{file_name}"
    with open(file_name) as of:
        jfile = json.load(of)
    return jfile


def getVals(params):
    p = dict()
    for param in params:
        p[param] = params[param].val
    return p


if __name__ == "__main__":
    file = 'environment.json'
    env_ = load_from_json(file)
    static_env = env_['static']
    dynamic_env = env_['dynamic']

    db_info = load_from_json(static_env['database_info_file'], static_env['database_info_path'])

    conf = {**static_env,
            **db_info}

    udfs = [load_from_json("10_intersect_np.json", static_env['udf_path']), load_from_json("10_intersect_pp.json", static_env['udf_path'])]
    tables_schema = list()
    for udf in udfs:
        for tb in udf['datasets']:
            if udf['datasets'][tb]['table_schema'] not in tables_schema:
                tables_schema.append(udf['datasets'][tb]['table_schema'])

    conf['tables_schema'] = tables_schema

    etl_process = select_driver(db_info['db']['etl_driver'])
    dc_json = load_from_json('docker-compose.yaml.json', 'db/cassandra')

    ansi_cat = static_env['ansible_catalog']
    scenarios = create_scenarios(dynamic_env)


    def main():
        tries = 2
        err_try_max = 4

        for udf in udfs:
            data_tries = dict()
            idx = 0
            err_try = 0

            while idx < tries:
                data = {
                    "data_acquisition_time": -1,
                    "etl_processing_time": -1.,
                    "overall_time": -1.
                }
                #

                if data is None:
                    err_try += 1
                    if err_try >= err_try_max:
                        raise RuntimeError("Too many errors.")
                    continue

                data_tries[idx] = data
                idx += 1
                with open("pd_process.temp.json", 'a') as cmd_file:
                    cmd_file.write(json.dumps({
                        "udf": udf['name'],
                        "tries": data_tries,
                        "scenario": "",
                        "timestamp": str(datetime.now())
                    }, indent=4))

            res = [{
                "udf": udf['name'],
                "tries": data_tries,
                "scenario": "",
                "timestamp": str(datetime.now())
            }]

            write_to_yaml(f"run_result_{datetime.now().strftime('%Y%m%d')}.yaml", res, ".", mode='a')

    main()

