import sys
import json


def write_to(file_name, data, output_path=None, mode='w'):
    if output_path is not None:
        file_name = f"{output_path}/{file_name}"
    with open(file_name, mode) as cmd_file:
        cmd_file.write(data)


def load_from(file_name, path=None):
    if path is not None:
        file_name = f"{path}/{file_name}"
    with open(file_name) as of:
        file_content = of.read()
    return file_content


if __name__ == '__main__':
    cluster_size = sys.argv[1]
    data_size = sys.argv[2]
    catalog = sys.argv[3]

    dc = load_from(f'docker-compose_sh{cluster_size}.yaml', ".")
    write_to('docker-compose.yaml', dc.format(data_size=data_size, cluster_size=cluster_size, catalog=catalog))

