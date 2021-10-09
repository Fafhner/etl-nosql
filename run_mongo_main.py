import io
import json
import logging
import subprocess
import sys
from datetime import datetime

import db.mongodb.etl.etl_process as etl
from pyspark.sql import SparkSession
import yaml
from pyarrow import fs
import uuid




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


def generate_hosts_file(manager, workers):
    hosts = """[cluster_node_manager]\n{manager}\n[cluster_node_workers]\n{workers}"""
    hosts = hosts.format(
        manager=manager,
        workers="\n".join(workers)
    )
    return hosts


def convert_tables_info(tables, config):
    tables_info = list()
    tb_infos = config['table_infos']
    for tb in tables:
        tb_info = tb_infos[tb]
        tables_info.append(tb_info['load'].format(
            namespace=config['namespace'],
            table=tb,
            path=config['db']['db_tables_path'] + "/" + str(config['scale']),
            file=tb_info['table']))
    return tables_info


def run_cmd(cmd, path, acc_error=None):
    out = subprocess.run(cmd, shell=True, cwd=path, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    print(out)
    if out.stderr != '':
        if acc_error is None or acc_error not in out.stderr:
            exit(-1)
    return out.stderr


def create_docker_compose(dc_json, size):
    parts = dc_json['parts'][0:size] + [dc_json['end']]
    return "\n".join(parts)


def create_ansible_cmd(notebook, hosts, user, password, path):
    def r_(env, grid, diff, tags):
        print(f"Running playbook - {notebook}")
        print(f"Grid: {grid}")
        print(f"Diff: {diff}")
        pb = f"ansible-playbook -i {hosts} -u {user} --extra-vars 'ansible_become_password={password} ansible_ssh_pass={password}'" \
             f" {notebook} --tags \"{tags}\""
        print("Running " + pb)
        return run_cmd(pb, path)

    return r_


def getVals(params):
    p = dict()
    for param in params:
        p[param] = params[param].val
    return p


def pretty_dict(dict_: dict, delim='|'):
    return delim.join([f"{k}={dict_[k]}" for k in dict_.keys()])


logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
print = rootLogger.info

py4j_logger = logging.getLogger('py4j')
py4j_logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

fileHandler = logging.FileHandler(f"spark_log_cass{datetime.now().strftime('%Y%m%d')}.output.log", mode='a')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

py4j_logger.addHandler(consoleHandler)
py4j_logger.addHandler(fileHandler)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No arguments given.")
        file = ""
        udf = ""
        exit(-1)
    else:
        file = sys.argv[1]

    conf = load_from_json(file)

    udfs = [load_from_json(udf, conf['udf_path']) for udf in conf['udfs']]

    params = {
        "data": conf['scale'],
        "o_mem":  conf['cache_size'],
        "cluster_size": conf['cluster_size']
    }

    spark = SparkSession \
        .builder \
        .appName(f"Cassandra_experiments_{datetime.now().strftime('%Y%m%d')}") \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.0.0') \
        .getOrCreate()

    hdfs = fs.HadoopFileSystem('192.168.55.11', port=9000, user='magisterka')
    tries = 4

    header = "uuid,ts,udf,rd,rk,po,time_etl,time_all\n"
    result_file = f"/home/magisterka/etl-nosql/result/RUN_etl_mongo.csv"
    write_to(result_file, header, mode='a')

    for udf in udfs:
        data_tries = dict()
        idx = 0
        id_ = str(uuid.uuid4())
        while idx < tries:

            try:
                result, result_df = etl.process(udf, spark, "mongodb://192.168.55.16")
                hdfs.delete_dir_contents("./tmp")
            except Exception as e:
                omit_udf = True
                logging.exception(e)
                break

            data_tries[idx] = result
            idx += 1
            a_data = f"{id_},{str(datetime.now())},{udf['name']},{params['cluster_size']},{params['data']},{params['o_mem']},{result['etl_processing_time']},{result['overall_time']}\n"
            result_df.write.parquet(f"output_df/{id_}/try_{idx}.parquet")
            write_to(result_file, a_data, mode='a')

