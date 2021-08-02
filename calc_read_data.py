import io
import json
import logging
import subprocess
import sys
from datetime import datetime

from grid import create_scenarios
from etl.etl_setup import select_driver
import state
from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
import yaml


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


logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)
print = rootLogger.info

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

fileHandler = logging.FileHandler(f"run_{datetime.now().strftime('%Y%m%d')}.output.log", mode='a')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No arguments given.")
        file = ""
        user = ""
        password = ""
        exit(-1)
    else:
        file = sys.argv[1]
        user = sys.argv[2]
        password = sys.argv[3]

    pos = int(sys.argv[4]) if len(sys.argv) >= 5 else None
    main_only = int(sys.argv[5]) if len(sys.argv) >= 6 else None
    env_ = load_from_json(file)
    static_env = env_['static']
    dynamic_env = env_['dynamic']

    db_info = load_from_json(static_env['database_info_file'], static_env['database_info_path'])

    conf = {**static_env,
            **db_info}

    udfs = [load_from_json(udf, static_env['udf_path']) for udf in static_env['udfs']]
    tables_schema = list()
    for udf in udfs:
        for tb in udf['datasets']:
            if udf['datasets'][tb]['table_schema'] not in tables_schema:
                tables_schema.append(udf['datasets'][tb]['table_schema'])

    conf['tables_schema'] = tables_schema

    etl_process = select_driver(db_info['db']['etl_driver']+"-hdfs")
    dc_json = load_from_json('docker-compose.yaml.json', 'db/cassandra')

    ansi_cat = static_env['ansible_catalog']
    scenarios = create_scenarios(dynamic_env)

    spark = SparkSession \
        .builder \
        .master("yarn") \
        .appName(f"Run_experiments_{datetime.now().strftime('%Y%m%d')}") \
        .getOrCreate()


    def create_files(conf, grid, diff):
        print("Generating hosts file")
        print(f"Grid: {grid}")
        print(f"Diff: {diff}")
        cluster_node_manager: str = conf['cluster']['node_manager']
        cluster_node_workers: list = conf['cluster']['node_workers']
        if cluster_node_manager in cluster_node_workers:
            cluster_node_workers.remove(cluster_node_manager)
        cluster_node_workers = cluster_node_workers[0:grid['cluster_size'].val - 1]

        hosts_file = generate_hosts_file(cluster_node_manager, cluster_node_workers)
        write_to('hosts', hosts_file, ansi_cat)

        print("Merge as ansible/group_vars/all.json")
        conf_all = {**conf,
                    **getVals(grid),
                    **db_info,
                    'cluster': {'node_manager': cluster_node_manager, 'node_workers': cluster_node_workers}
                    }

        write_to('all.json', json.dumps(conf_all, indent=4), ansi_cat + "/group_vars")

        print("Create tables_schema/load file")
        load_file_data = convert_tables_info(conf['tables_schema'], conf_all)
        write_to('load', "\n".join(load_file_data), "db/cassandra/tables_schema")


    def main(env, grid, diff):
        cluster = Cluster([env["cluster"]["node_manager"]], connect_timeout=20)
        tries = 12
        err_try_max = 4

        for udf in udfs:
            data_tries = dict()
            idx = 0
            err_try = 0

            while idx < tries:
                data = etl_process(cluster, udf, spark, grid['cluster_size'].val, grid['scale'].val)

                if data is None:
                    err_try += 1
                    if err_try >= err_try_max:
                        raise RuntimeError("Too many errors.")
                    continue

                data_tries[idx] = data
                idx += 1

            res = [{
                "udf": udf['name'],
                "tries": data_tries,
                "scenario": getVals(grid),
                "timestamp": str(datetime.now())
            }]

            write_to_yaml(f"result/data_read_results_{datetime.now().strftime('%Y%m%d')}.yaml", res, ".", mode='a')

        cluster.shutdown()


    do_once_nodes = [
        state.Node('Prepare', create_ansible_cmd('prepare.yaml', 'hosts_all', user, password, ansi_cat))
    ]
    preprocess_nodes = [
        state.Node('create_files', create_files)
    ]

    flow_tree = [
        {
            "name": 'all',
            "if": lambda _, grid, diff: True,
            "then": ['tag_prepare', 'tag_create_table_data', 'tag_files', 'tag_init_swarm', 'tag_deploy_stack']
        },
    ]

    sm = state.StateMachine(rootLogger)
    sm.setDoOnlyOnce(do_once_nodes)
    sm.addNodes(preprocess_nodes)
    sm.setFlowTree(flow_tree)
    sm.setMain(main)
    sm.ansbile_f = create_ansible_cmd('load_data.yaml', 'hosts', user, password, ansi_cat)

    sm.loop(conf, scenarios, pos, main_only)

    do_once_nodes[0].do(conf, None, None, 'all')
    create_ansible_cmd('hadoop-stop.yaml', 'hosts', user, password, ansi_cat)(None, None, None, 'all')
