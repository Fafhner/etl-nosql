
from datetime import  datetime
from cassandra.cluster import Cluster, Session
import pandas as pd
from etl.etl_setup import cassandra_process
import json

from create import create_scenarios
from etl.etl_setup import select_driver
import state

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


def load_from(file_name, path=None):
    if path is not None:
        file_name = f"{path}/{file_name}"
    with open(file_name) as of:
        jfile = json.load(of)
    return jfile


if __name__ == "__main__":
    file = 'environment.json'
    env_ = load_from(file)
    static_env = env_['static']
    dynamic_env = env_['dynamic']

    db_info = load_from(static_env['database_info_file'], static_env['database_info_path'])

    conf = {**static_env,
            **db_info}

    udfs = [load_from(udf, static_env['udf_path']) for udf in static_env['udfs']]
    tables_schema = list()
    for udf in udfs:
        for tb in udf['datasets']:
            if udf['datasets'][tb]['table_schema'] not in tables_schema:
                tables_schema.append(udf['datasets'][tb]['table_schema'])

    conf['tables_schema'] = tables_schema

    etl_process = select_driver(db_info['db']['etl_driver'])
    dc_json = load_from('docker-compose.yaml.json', 'db/cassandra')

    ansi_cat = static_env['ansible_catalog']
    scenarios = create_scenarios(dynamic_env)


    def main():
        cluster = Cluster([conf["cluster"]["node_manager"]],  connect_timeout=20)
        for udf in udfs:

            data = etl_process(cluster, udf)

            res = {
                "udf": udf['name'],
                "steps": data['steps'],
                "scenario": ""
            }
            print("Result:")
            print(json.dumps(res, indent=4))
            write_to(f"result/run_{datetime.now().strftime('%Y%m%d')}_{udf['name']}.result.json",
                     json.dumps(res, indent=4), ".", mode='a')

        cluster.shutdown()
    main()
