import sys
from datetime import datetime

from util.grid import create_scenarios
from util import state
from util.util import *


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
    if len(sys.argv) != 4:
        print(f"Wrong number of parameters. Expected 3 got {len(sys.argv) - 1}.")
        user, password, conf_file_str = "", "", ""
        exit(-1)
    else:
        user, password, conf_file_str = sys.argv[1], sys.argv[2], sys.argv[3]

    env_ = load_from_json(conf_file_str)
    conf = env_['static']
    conf_dynamic = env_['dynamic']

    udfs = [load_from_json(udf, conf['udf_path']) for udf in conf['udfs']]
    ansi_catalog = conf['ansible_load_data_path']
    ansi_file = conf['ansible_load_data_file']
    scenarios = create_scenarios(conf_dynamic)


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


    def _main_(_, __, ___):
        print("\n\n\nLoading ended...\n\n\n")
        return None

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


    sm.setMain(_main_)
    sm.ansbile_f = create_ansible_cmd(ansi_file, 'hosts', user, password, ansi_catalog)

    sm.loop(conf, scenarios)