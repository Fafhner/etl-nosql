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


def generate_hosts_file(manager, workers):
    hosts = """[cluster_node_manager]\n{manager}\n[cluster_node_workers]\n{workers}"""
    hosts = hosts.format(
        manager=manager,
        workers="\n".join(workers)
    )
    return hosts


def convert_tables_info(tables, config):
    tables_info = list()
    for tb in tables:
        for tb_info in config['table_infos']:
            if tb in tb_info['tables']:
                tables_info.append(tb_info['load'].format(
                    namespace=config['namespace'],
                    table=tb,
                    path=config['db']['db_tables_path'] + "/" + str(config['scale']),
                    file=tb_info['table']))
    return tables_info


def run_script(script_name, path, acc_error=None):
    out = subprocess.run(f'bash {script_name};', shell=True, cwd=path, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    if out.stderr != '':
        if acc_error is None or acc_error not in out.stderr:
            exit(-1)


def run_cmd(cmd, path, acc_error=None):
    out = subprocess.run(cmd, shell=True, cwd=path, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    print(out)
    if out.stderr != '':
        if acc_error is None or acc_error not in out.stderr:
            exit(-1)


def create_docker_compose(dc_json, size):
    parts = dc_json['parts'][0:size] + [dc_json['end']]
    return "\n".join(parts)


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

    env = load_from(file)
    static_env = env['static']
    dynamic_env = env['dynamic']

    db_info = load_from(static_env['database_info_file'], static_env['database_info_path'])
    etl_process = select_driver(db_info['db']['etl_driver'])
    dc_json = load_from('docker-compose.yaml.json', 'db/cassandra')
    print("-" * 20)

    active_tags = {
        "create_tables": True,
        "create_cluster": True,
        "leave_cluster": True,
        "restore_files": True,
        "create_cluster_network": True,
        "backup_files": True,
        "docker_stack_deploy": True,
        "create_namespace": True,
        "create_table_schema": True,
        "load_data": True
    }

    ansi_cat = static_env['ansible_catalog']
    scenarios = create_scenarios(dynamic_env)

    print("Coping files")
    # run_cmd(f"ansible-playbook -i hosts_all -u {user} --extra-vars 'ansible_become_pass={password}' copy.yaml", ansi_cat)

    for scenario_key in scenarios.keys():
        scenario = scenarios[scenario_key]
        udf = load_from(scenario['udf'], static_env['udf_path'])

        # 1 ########################
        print("Generating hosts file")
        cluster_node_manager: str = static_env['cluster']['node_manager']
        cluster_node_workers: list = static_env['cluster']['node_workers']
        if cluster_node_manager in cluster_node_workers:
            cluster_node_workers.remove(cluster_node_manager)
        cluster_node_workers = cluster_node_workers[0:scenario['cluster_size'] - 1]
        hosts_file = generate_hosts_file(cluster_node_manager, cluster_node_workers)

        write_to('hosts', hosts_file, ansi_cat)

        # 2 ########################
        conf_all = {**static_env, **scenario, **db_info, **active_tags,
                    'cluster': {'node_manager': cluster_node_manager, 'node_workers': cluster_node_workers}}

        conf_all['data_generator']['tables'] = [tb for tb in udf['datasets']]
        conf_all['tables_schema'] = [udf['datasets'][tb]['table_schema'] for tb in udf['datasets']]

        print("Generating group_var/all.json file")
        write_to('all.json', json.dumps(conf_all, indent=4), ansi_cat + "/group_vars")

        print("   ")
        load_file_data = convert_tables_info(conf_all['tables_schema'], conf_all)
        write_to('load', "\n".join(load_file_data), "db/cassandra/tables_schema")

        print("Create docker-compose")
        dc = create_docker_compose(dc_json, scenario['cluster_size'])
        write_to('docker-compose.yaml', dc, 'db/cassandra')
        # 3 ########################
        print("Running ansible")
        # run_cmd(f"ansible-playbook -i hosts -u {user} --extra-vars 'ansible_ssh_pass={password}' run.yaml", ansi_cat)
