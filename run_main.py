import json
import logging
import subprocess
import sys
from datetime import datetime

from util.grid import create_scenarios
from util import state


def write_to(file_name, data, output_path=None, mode='w'):
    if output_path is not None:
        file_name = f"{output_path}/{file_name}"
    with open(file_name, mode) as cmd_file:
        cmd_file.write(data)


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


def run_cmd(cmd, path, acc_error=None):
    out = subprocess.run(cmd, shell=True, cwd=path, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)

    for stdout_line in out.stdout.splitlines():
        logging.info(stdout_line.strip())

    for stderr_line in out.stderr.splitlines():
        logging.warning(stderr_line.strip())

    if out.stderr != '':
        if acc_error is None or acc_error not in out.stderr:
            pass
            # exit(-1)
    return out


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
rootLogger.setLevel(logging.DEBUG)
print = rootLogger.info

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

fileHandler = logging.FileHandler(f"logs/run_{datetime.now().strftime('%Y%m%d')}.output.log", mode='a')
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

    ansi_cat = static_env['ansible_catalog']
    scenarios = create_scenarios(dynamic_env)

    print(f"------ Scenarios: {len(scenarios)} ---------------")


    def create_files(conf, grid, diff):
        print("Generating hosts file")
        print(f"Grid: {grid}")
        print(f"Diff: {diff}")
        cluster_node_manager: str = conf['cluster']['node_manager']
        cluster_node_workers: list = conf['cluster']['node_workers']
        if cluster_node_manager in cluster_node_workers:
            cluster_node_workers.remove(cluster_node_manager)
        cluster_node_workers = cluster_node_workers[0:grid['cluster_size'].val]

        hosts_file = generate_hosts_file(cluster_node_manager, cluster_node_workers)
        write_to('hosts', hosts_file, ansi_cat)

        print("Merge as ansible/group_vars/all.json")
        conf_all = {**conf,
                    **getVals(grid),
                    **db_info,
                    'cluster': {'node_manager': cluster_node_manager, 'node_workers': cluster_node_workers}
                    }

        write_to('all.json', json.dumps(conf_all, indent=4), ansi_cat + "/group_vars")


    database = conf['database']
    if database == 'cassandra':
        spark_cmd = \
            'spark-submit --master "yarn" ' \
            '--driver-memory 4G ' \
            '--executor-cores 2 ' \
            '--conf spark.cassandra.connection.host=192.168.55.16 ' \
            '--packages com.datastax.spark:spark-cassandra-connector_2.12:3.1.0 ' \
            '--conf spark.sql.extensions=com.datastax.spark.connector.CassandraSparkExtensions ' \
            '--conf spark.sql.dse.search.enableOptimization=Off ' \
            '--conf spark.sql.dse.search.autoRatio=0.0 ' \
            '--conf spark.cassandra.input.fetch.sizeInRows=10000 ' \
            '/home/magisterka/etl-nosql/run_cass_test.py ' \
            '/home/magisterka/etl-nosql/db/cassandra/ansible/group_vars/all.json '
    else:
        spark_cmd = \
            'spark-submit --master "yarn" ' \
            '--packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 ' \
            '/home/magisterka/etl-nosql/run_mongo_test.py ' \
            '/home/magisterka/etl-nosql/db/mongodb/ansible/group_vars/all.json '



    def main(env, grid, diff):
        for udf in static_env['udfs']:
            run_cmd(spark_cmd + " " + udf, path=".")


    do_once_nodes = [
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
    sm.setMain(main)
    sm.ansbile_f = create_ansible_cmd('main.yaml', 'hosts', user, password, ansi_cat)

    sm.loop(conf, scenarios, pos, main_only)
