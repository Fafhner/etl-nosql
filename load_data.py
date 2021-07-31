import io
import json
import logging
import subprocess
import sys
from datetime import datetime

from grid import create_scenarios
import state
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
        user = sys.argv[1]
        password = sys.argv[2]

    static_env = {
        "cluster": {
            "node_manager": "192.168.55.20",
            "node_workers": [
                "192.168.55.16",
                "192.168.55.17",
                "192.168.55.18",
                "192.168.55.19",
                "192.168.55.20"
            ]
        },
        "database_info_path": "~/etl-nosql/db/cassandra",
        "udf_path": "~/etl-nosql/db/cassandra/udf",
        "database_info_file": "cassandra.info.json",
        "docker_compose_path": "~/etl-nosql/db/cassandra",
        "docker_compose_file_gen": "~/etl-nosql/db/cassandra/",
        "docker_compose_file": "~/etl-nosql/db/cassandra/docker-compose.yaml",
        "ansible_catalog": "~/etl-nosql/ansible-load",
        "generate_scripts_only": False,
        "tables_schema": [
            "date_dim",
            "store_sales",
            "catalog_sales",
            "web_sales",
            "warehouse",
            "customer"
        ]

    }

    dynamic_env = {
        "scale": {
            "context": "table_data",
            "priority": 999,
            "data": [1, 3, 5, 10, 15, 35]
        },
        "cluster_size": {
            "context": "cluster",
            "priority": 998,
            "data": [3, 4, 5]
        },
        "rep_factor": {
            "context": "db-keyspace",
            "priority": 2,
            "data": [3]
        },
        "java_xms": {
            "context": "db-file",
            "priority": 2,
            "data": [
                5000
            ]
        }

    }

    db_info = load_from_json(static_env['database_info_file'], static_env['database_info_path'])

    conf = {**static_env,
            **db_info}

    udfs = [load_from_json(udf, static_env['udf_path']) for udf in static_env['udfs']]

    dc_json = load_from_json('docker-compose.yaml.json', 'db/cassandra')

    ansi_cat = static_env['ansible_catalog']
    scenarios = create_scenarios(dynamic_env)


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

        print("Create docker-compose")
        dc = create_docker_compose(dc_json, grid['cluster_size'].val)
        dc = dc.format(cluster_size=grid['cluster_size'].val, data_size=grid['scale'].val)
        write_to('docker-compose.yaml', dc, '~/etl-nosql/db/cassandra')


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
            "then": ['all']
        },
    ]

    sm = state.StateMachine(rootLogger)
    sm.setDoOnlyOnce(do_once_nodes)
    sm.addNodes(preprocess_nodes)
    sm.setFlowTree(flow_tree)


    def _main_(_, __, ___):
        print("\n\n\nLoading ended...\n\n\n")
        return None


    sm.setMain(_main_)
    sm.ansbile_f = create_ansible_cmd('load_data.yaml', 'hosts', user, password, ansi_cat)

    sm.loop(conf, scenarios)

    do_once_nodes[0].do(conf, None, None, 'all')