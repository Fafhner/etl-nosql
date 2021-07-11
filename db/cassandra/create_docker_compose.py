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
        jfile = json.load(of)
    return jfile


if __name__ == '__main__':
    size = int(sys.argv[1])
    dc_json = load_from('docker-compose.yaml.json', '.')
    parts = dc_json['parts'][0:size] + [dc_json['end']]
    write_to('docker-compose.yaml', "\n".join(parts))

