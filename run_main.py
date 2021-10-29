import sys
from datetime import datetime

from util.grid import create_scenarios
from util import state
from util.util import *


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
    conf = env_['static']
    conf_dynamic = env_['dynamic']


    udfs = [load_from_json(udf, conf['udf_path']) for udf in conf['udfs']]
    ansi_catalog = conf['ansible_catalog']

    scenarios = create_scenarios(conf_dynamic)


    print(f"------ Scenarios: {len(scenarios)} ---------------")


    def create_files(conf, grid, diff):
        print("Generating hosts file")
        print(f"Grid: {grid}")
        print(f"Diff: {diff}")
        cluster_node_manager: str = conf['cluster']['node_manager']
        cluster_node_workers: list = conf['cluster']['node_workers']
        if cluster_node_manager in cluster_node_workers:
            cluster_node_workers.remove(cluster_node_manager)

        hosts_file = generate_hosts_file(cluster_node_manager, cluster_node_workers)
        write_to('hosts', hosts_file, ansi_catalog)

        print("Merge as ansible/group_vars/all.json")
        conf_all = {**conf,
                    **getVals(grid),
                    'cluster': {'node_manager': cluster_node_manager, 'node_workers': cluster_node_workers}
                    }

        write_to('all.json', json.dumps(conf_all, indent=4), ansi_catalog + "/group_vars")


    database = conf['database']
    spark_cmd = conf['spark_cmd']

    def main_f():
        if database == 'mongodb':
            def main(env, grid, diff):
                for udf in conf['udfs']:
                    run_cmd(f"{spark_cmd} {ansi_catalog}/group_vars/all.json {udf} {conf['loops']} {conf['output']}", path=".")
        else:
            def main(env, grid, diff):
                for udf in conf['udfs']:
                    for i in range(conf['loops']):
                        run_cmd(f"{spark_cmd} {ansi_catalog}/group_vars/all.json {udf} {i} {conf['output']}", path=".")

        return main

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
    sm.setMain(main_f())

    sm.ansbile_f = create_ansible_cmd('main.yaml', 'hosts', user, password, ansi_catalog)

    sm.loop(conf, scenarios, pos, main_only)
