import json
import subprocess
import sys
import logging
import os
import time

from create import create_scenarios, create_cluster_script, create_tables_script, create_db_config_script, \
    create_docker_setup, create_yaml, create_load_tables_script
from etl.etl_setup import select_driver
from grid import GridDiff
from state import StateMachine

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
print = rootLogger.info

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


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


def run_script(script_name, path, acc_error=None):
    out = subprocess.run(f'bash {script_name};', shell=True, cwd=path, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    if out.stderr != '':

        if acc_error is None or acc_error not in out.stderr:
            rootLogger.error(f"Error -  {out.stderr}")
            exit(-1)
        rootLogger.warning(f"Warning -  {out.stderr}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No arguments given.")
        file = "environment.json"
        # exit(-1)
    else:
        file = sys.argv[1]

    env = load_from(file)

    fileHandler = logging.FileHandler("{0}/{1}.log".format(env['output_path'], env['name'] + '.output'), mode='w')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    state_machine = StateMachine(
        links={
            'START': ['CREATE_SCENARIOS'],
            'CREATE_SCENARIOS': ['NEW_SCENARIO'],
            'NEW_SCENARIO': ['CREATE_SCRIPTS', 'STOP'],
            'CREATE_SCRIPTS': ['NEW_SCENARIO', 'CREATE_TABLES', 'CREATE_FILES', 'CHANGE_FILES',
                               'CREATE_CLUSTER', 'DEPLOY_STACK', 'LOAD_DATA', 'RUN_TEST'],
            'CREATE_TABLES': ['CHANGE_FILES',
                              'CREATE_CLUSTER', 'DEPLOY_STACK', 'LOAD_DATA', 'RUN_TEST', 'STOP'],
            'CHANGE_FILES': ['CREATE_CLUSTER', 'DEPLOY_STACK', 'LOAD_DATA', 'RUN_TEST'],
            'CREATE_CLUSTER': ['DEPLOY_STACK', 'LOAD_DATA', 'RUN_TEST'],
            'DEPLOY_STACK': ['LOAD_DATA', 'RUN_TEST'],
            'LOAD_DATA': ['RUN_TEST'],
            'RUN_TEST': ['NEW_SCENARIO', 'STOP'],
        }
    )

    grid_diff = GridDiff()
    state_machine.state = 'START'

    scenarios = create_scenarios(env['grid_params'])
    state_machine.updateToState('CREATE_SCENARIOS')

    conf = dict()
    output = env['output_path']
    conf['cluster_start'] = env['name'] + ".cluster_start.sh"
    conf['cluster_stop'] = env['name'] + ".cluster_stop.sh"
    conf['tables_create'] = env['name'] + ".table_create.sh"
    conf['db_apply'] = env['name'] + ".db_fapply.sh"
    conf['db_restore'] = env['name'] + ".db_frestore.sh"
    conf['docker_compose'] = "docker-compose-" + env['etl_driver'] + ".yml"
    conf['stack_deploy'] = env['name'] + ".stack_deploy.sh"
    conf['stack_rm'] = env['name'] + ".stack_rm.sh"
    conf['db_schema'] = env['tables_load_name']
    conf['load_data'] = env['name'] + ".load_data.sh"
    conf['rm_data'] = env['name'] + ".rm_data.sh"

    print("CREATING TEST ENVIRONMENT")
    print(f"NUMBER OF SCENARIOS - {len(scenarios)}")
    print(f"OUTPUT: {output}")
    print(f"Cluster start script name: {conf['cluster_start']}")
    print(f"Cluster stop script name: {conf['cluster_stop']}")
    print(f"Tables creation script name: {conf['tables_create']}")
    print(f"Changing database files script name: {conf['db_apply']}")
    print(f"Restoring database files script name: {conf['db_restore']}")
    print(f"Reading db info file: {env['database_info_file']}")
    db_info = load_from(env['database_info_file'], env['database_info_path'])
    print(f"Selected driver: {env['etl_driver']}")
    etl_process = select_driver(env['etl_driver'])

    print("-" * 20)

    selected_nodes = []
    for scenario_key in scenarios.keys():
        scenario = scenarios[scenario_key]
        state_machine.updateToState('NEW_SCENARIO')

        print(f"SCENARIO {scenario_key} - {scenario}")
        scenario_diff = grid_diff.nextState(scenario)

        if scenario_diff['scale']:
            print("Generating tables_schema creation script.")
            create_tables = create_tables_script(tool_path=env['table_gen_path'],
                                                 tool_name=env['table_gen_tool'],
                                                 scale=scenario['scale'],
                                                 tables=env['table_gen_tables'],
                                                 **env['table_gen_args'])
            write_to(conf['tables_create'], create_tables, output)
        else:
            print("Tables already generated. Ommiting.")

        if scenario_diff['cluster_size']:
            print("Generating cluster configuration script.")
            start_cluster, stop_cluster, selected_nodes = create_cluster_script(
                cluster_ips=env['cluster_available_nodes'],
                cluster_size=scenario['cluster_size'],
                manager_ip=env['manager_node_ip'],
                user=env['ssh_user'])

            write_to(conf['cluster_start'], start_cluster, output)
            write_to(conf['cluster_stop'], stop_cluster, output)
        else:
            print("Cluster configured. Ommiting.")

        if scenario_diff['row_cache_size_in_mb']:
            print("Generating db configuration scripts.")
            apply_changes = ""
            restore_changes = ""
            for file in db_info['create']:
                argvals = []
                for args in file['args']:
                    for arg_key in args:
                        if arg_key in scenario:
                            argvals.append((args[arg_key], scenario[arg_key]))
                ac, rc = create_db_config_script(nodes=selected_nodes, user=env['ssh_user'],
                                                 file_name=file['file_name'],
                                                 file_path=file['file_path'], argvals=argvals)
                apply_changes += ac
                restore_changes += rc

            write_to(conf['db_apply'], apply_changes, output)
            write_to(conf['db_restore'], restore_changes, output)
        else:
            print("DB configuration already exist. Ommiting.")

        if scenario_diff['row_cache_size_in_mb']:
            print("Generating docker .yaml")
            yaml_file = create_yaml(db_info=db_info, nodes=selected_nodes)
            write_to(conf['docker_compose'], yaml_file, output)
        else:
            print("Yaml already generated. Ommiting.")

        if scenario_diff['row_cache_size_in_mb']:
            print("Generating docker stack deploy and remove scripts.")
            # TODO: YAML generated in ../scripts but stack deployment through ssh and manager node ip

            stack_deploy, stack_rm = create_docker_setup(compose_file=conf["docker_compose"],
                                                         compose_file_path=".",
                                                         docker_network_name=db_info['docker_network_name'],
                                                         stack_name=env['docker_stack_name'],
                                                         manager_node=env['manager_node_ip'],
                                                         user=env['ssh_user'])
            write_to(conf['stack_deploy'], stack_deploy, output)
            write_to(conf['stack_rm'], stack_rm, output)
        else:
            print("Stack already deployed. Ommiting.")

        if scenario_diff['row_cache_size_in_mb'] or scenario_diff['scale']:
            print("Generating tables_schema loading script.")
            cmd_file_schema, cmd_load, cmd_drop = create_load_tables_script(
                stack_name=env['docker_stack_name'],
                db_info=db_info,
                tables_data_path=f"{env['tables_dest_path']}/{scenario['scale']}",
                tables_load_catalog=f"{env['tables_dest_path']}/{env['tables_load_catalog']}",
                tables_load_name=env['tables_load_name'])
            # write_to(conf['db_schema'], cmd_file_schema, output)

            write_to(conf['db_schema'], cmd_file_schema, f"{os.environ['HOME']}/etl-nosql/db/tables_schema/load/cassandra")
            write_to(conf['load_data'], cmd_load, output)
            write_to(conf['rm_data'], cmd_drop, output)

        state_machine.updateToState('CREATE_SCRIPTS')

        if env['generate_scripts_only'] is False:
            # TODO RUN EXPERIMENTS
            ############################################################
            print("RUNNING SCRIPTS")
            if scenario_diff['scale']:
                print(f"Creating tables_schema - running {conf['tables_create']}")
                try:
                    run_script(conf['tables_create'], env['output_path'], acc_error="exists")
                finally:
                    write_to('state_machine.json',
                             json.dumps(state_machine.saveStateAsDict(), sort_keys=True, indent=4),
                             ".")
                    exit(-1)
                state_machine.updateToState('CREATE_TABLES')

            if scenario_diff['row_cache_size_in_mb']:
                print(f"Applying changes to files - running {conf['db_apply']}")
                try:
                    run_script(conf['db_apply'], env['output_path'])
                finally:
                    write_to('state_machine.json',
                             json.dumps(state_machine.saveStateAsDict(), sort_keys=True, indent=4),
                             ".")
                    exit(-1)
                state_machine.updateToState('CHANGE_FILES')
            if scenario_diff['cluster_size']:
                print(f"Creating cluster - running {conf['cluster_start']}")
                try:
                    run_script(conf['cluster_start'], env['output_path'])
                finally:
                    write_to('state_machine.json',
                             json.dumps(state_machine.saveStateAsDict(), sort_keys=True, indent=4),
                             ".")
                    exit(-1)

            state_machine.updateToState('CREATE_CLUSTER')

            if scenario_diff['row_cache_size_in_mb']:
                print(f"Deploying docker cluster - running {conf['stack_deploy']}")
                try:
                    run_script(conf['stack_deploy'], env['output_path'], "exists")
                finally:
                    write_to('state_machine.json',
                             json.dumps(state_machine.saveStateAsDict(), sort_keys=True, indent=4),
                             ".")
                    exit(-1)

            state_machine.updateToState('DEPLOY_STACK')

            time.sleep(10)
            print(f"Loading data to db - running {conf['load_data']}")
            try:
                run_script(conf['load_data'], env['output_path'])
            finally:
                write_to('state_machine.json',
                         json.dumps(state_machine.saveStateAsDict(), sort_keys=True, indent=4),
                         ".")
                exit(-1)

            state_machine.updateToState('LOAD_DATA')

            # TODO RUN process
            print(f"Running experiment with driver - {env['etl_driver']}")
            try:
                result = etl_process(selected_nodes, "udf/10_intersect_1.json")
            finally:
                write_to('state_machine.json',
                         json.dumps(state_machine.saveStateAsDict(), sort_keys=True, indent=4),
                         ".")
                exit(-1)

            raport = {"scenario": scenario, "result": result}

            write_to("cassandra_result__.json", str(raport), ".", mode='a')
            write_to("cassandra_result.json", json.dumps(raport, sort_keys=True, indent=4), ".", mode='a')
            state_machine.updateToState('RUN_TEST')

            print(f"CLEANING")
            print(f"Removing stack - running {conf['stack_rm']}")
            run_script(conf['stack_rm'], env['output_path'])

            print(f"Destroying cluster - running {conf['cluster_stop']}")
            run_script(conf['cluster_stop'], env['output_path'])

            print(f"Restoring files - running {conf['db_restore']}")
            run_script(conf['db_restore'], env['output_path'])






# TODO Nodes
# TODO State Machine
# TODO ETL
