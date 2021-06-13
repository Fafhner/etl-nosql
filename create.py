from grid import GridParam, Grid
import os


def create_scenarios(grid_params):
    grid_params = [GridParam(pk, **grid_params[pk]) for pk in grid_params]
    grid = Grid()
    grid.params = grid_params
    return grid.generate_scenarios()


def create_cluster_script(cluster_ips, cluster_size, manager_ip, user):
    selected_nodes = [manager_ip]
    if manager_ip in cluster_ips:
        cluster_size -= 1
        cluster_ips.remove(manager_ip)

    cmd = '\necho "docker-swarm init"\n'
    cmd += f'sshpass -e ssh -o StrictHostKeyChecking=no {user}@{manager_ip} "docker swarm init" \n'
    rm_cluster_cmd = ""
    if cluster_size > 0:

        cmd += f'TOKEN=$(sshpass -e ssh -o StrictHostKeyChecking=no {user}@{manager_ip} "docker swarm join-token -q worker")\n'
        for c_ip in cluster_ips:
            cmd += f'echo "docker-swarm join {c_ip}"\n'
            cmd += f'sshpass -e ssh -o StrictHostKeyChecking=no {user}@{c_ip} "docker swarm join --token $TOKEN ' \
                   + manager_ip + ':2377"\n'
            cluster_size -= 1
            rm_cluster_cmd += f'sshpass -e ssh -o StrictHostKeyChecking=no {user}@{c_ip} "docker swarm leave" \n'
            selected_nodes.append(c_ip)
            if cluster_size <= 0:
                break

    cmd += "wait \n sleep 1 \n"
    rm_cluster_cmd += "wait \n"
    rm_cluster_cmd += f'sshpass -e ssh -o StrictHostKeyChecking=no {user}@{manager_ip} "docker swarm leave --force" \n'
    return cmd, rm_cluster_cmd, selected_nodes


def create_tables_script(tool_path, tool_name, scale, tables, **kwargs):
    tool = "{tool_name} -DIR {dir}/{scale} -SCALE {scale} -TERMINATE {terminate} -RNGSEED {rngseed} " \
           "-FORCE {force} -DISTRIBUTIONS {distr}".format(tool_name=tool_name, scale=scale, **kwargs)

    cmd = "mkdir -p {dir}/{scale} \n".format(scale=scale, **kwargs)
    cmd += f"cd {tool_path} \n"

    if len(tables) != 0:
        for table in tables:
            cmd += tool + f" -TABLE {table}" + " \n"
    else:
        cmd += tool + "\n"
    cmd += "wait \n sleep 1 \n"
    return cmd


def __replace_param_in_file(file_name, file_path, arg, value):
    return f"sed -i 's/{arg}.*/{arg}={value}/g' {file_path}/{file_name}"


def __backup_file(file_name, file_path):
    return f"cp {file_path}/{file_name} {file_path}/{file_name}.backup"


def __restore_file_from_backup(file_name, file_path):
    return f"cp {file_path}/{file_name}.backup {file_path}/{file_name}"


def create_db_config_script(nodes, user, file_name, file_path, argvals):
    cmd_apply = ""
    cmd_backup = ""
    cmd_restore = ""
    for node in nodes:
        cmd_backup += f'sshpass -e ssh -o StrictHostKeyChecking=no {user}@{node} "' + \
                      __backup_file(file_name, file_path) + '" \n'
        cmd_restore += f'sshpass -e ssh -o StrictHostKeyChecking=no {user}@{node} "' + \
                       __restore_file_from_backup(file_name, file_path) + '" \n'

        for arg, value in argvals:
            cmd_apply += f'sshpass -e ssh -o StrictHostKeyChecking=no {user}@{node} "' + \
                         __replace_param_in_file(file_name, file_path, arg, value) + '" \n'

    cmd_backup += "wait \n sleep 1\n"
    cmd_apply += "wait \n sleep 1\n"
    cmd_restore += "wait \n sleep 1\n"
    return cmd_backup + cmd_apply, cmd_restore


def create_docker_setup(compose_file, compose_file_path, docker_network_name, stack_name, manager_node, user):
    cmd = f"docker network create -d overlay {docker_network_name}" + '\n'
    cmd += f"docker stack deploy -c {compose_file_path}/{compose_file} {stack_name}" + '\n'
    cmd_rm = f"docker stack rm {stack_name}" + '\n'

    cmd += "wait \nsleep 30\n"
    cmd_rm += "wait \nsleep 1\n"
    return cmd, cmd_rm


template_node = """
  {service_name}:
    image: {image}
    ports:
{ports}
    volumes:
{volumes}
    networks:
{network}
"""

template_service = """
version: '3'
services:
  {services}

networks:
  {network}:
    external:
      name: {network_name}
"""


def create_yaml(db_info, nodes):
    service_name_template = f"{db_info['service_name']}" + "{id}"
    sp6_template = "      {data}"

    network = db_info['docker_network']
    network_name = db_info['docker_network_name']
    db_ports = db_info['ports']
    db_volumes = db_info['volumes']
    db_env = db_info['environment']

    cid = 0
    services_names = []
    service_nodes = []
    for node in nodes:
        service_name = service_name_template.format(id=cid)
        services_names.append(service_name)

        env, ports, volumes = [], [], []

        # for env_key in db_env:
        #     if env_key in db_info['eval']:
        #         env_val = eval(db_info['eval'][env_key])
        #     else:
        #         env_val = db_env[env_key]
        #     if env_val != '':
        #         env.append(sp6_template.format(data=f'{env_key}: "{env_val}"'))

        for port in db_ports:
            ports.append(sp6_template.format(data=f'- "{port}"'))

        for vol in db_volumes:
            volumes.append(sp6_template.format(data=f'- "{vol}"'))

        sn = template_node.format(service_name=service_name, image=db_info['docker_image'],
                                  environment="\n".join(env), ports="\n".join(ports),
                                  volumes="\n".join(volumes),
                                  network=sp6_template.format(data=f"- {network}"))

        service_nodes.append(sn)
        cid += 1

    return template_service.format(services="\n".join(service_nodes), network=network,
                                   network_name=network_name)


def create_copy_db_info_script(db_info):
    cmd = f"mkdir -p {db_info['service_name']}\n"


def create_load_tables_script(stack_name, db_info, tables_data_path, tables_load_catalog, tables_load_name):
    cmd = f'container_id=$(docker ps -lqf "name=^{stack_name}*")\n'
    cmd_file_schema = ""
    cmd_load = cmd

    cmd_drop = cmd

    exec_file = db_info['exec_file']
    exec_string = db_info['exec_string']

    cmd_load += f'docker exec "$container_id" {exec_string.format(str=db_info["keyspace"])}\n'

    for tb_info in db_info['table_infos']:
        cmd_file_schema += tb_info["load"].format(path=tables_data_path, file=tb_info["table"]) + "\n"


        cmd_load += 'docker exec "$container_id" ' + \
                    f'{exec_file.format(load_path=f"{tables_load_catalog}", load_file=tb_info["create"][0])}\n'
        cmd_drop += 'docker exec "$container_id" ' + f'"{exec_string.format(str=tb_info["drop"])}" \n'

    cmd_load += 'docker exec "$container_id" ' + \
                f'{exec_file.format(load_path=f"{tables_load_catalog}", load_file=tables_load_name)}\n'
    cmd += 'wait \nsleep 1 \n'
    return cmd_file_schema, cmd_load, cmd_drop
