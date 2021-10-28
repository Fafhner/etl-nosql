import os
import json
import sys
from datetime import datetime


def line_to_json(line: str, schema):
    line_split = line.strip().split('|')

    schema_cols = schema['cols']
    line_json = []
    for i, split in enumerate(line_split):
        col_type = schema_cols[i]['type']
        col_name = schema_cols[i]['col_name']
        if split != '':
            if col_type in ['varchar', 'ascii']:
                line_json.append(f'"{col_name}": "{split}"')
            elif col_type == 'date':
                date = datetime.strptime(split, '%Y-%m-%d').isoformat() + 'Z'
                line_json.append(f'"{col_name}": {{ "$date": "{date}" }}')
            elif col_type == 'bigint':
                line_json.append(f'"{col_name}": {{ "$numberLong": "{split}" }}')
            elif col_type == 'decimal':
                line_json.append(f'"{col_name}": {{ "$numberDecimal": "{split}" }}')
            else:
                line_json.append(f'"{col_name}": {split}')
        else:
            line_json.append(f'"{col_name}": null')

    return "{" + ", ".join(line_json) + "}\n"


if __name__ == '__main__':
    data_size = sys.argv[1]
    table = sys.argv[2]
    schema_path = sys.argv[3]
    data_path = sys.argv[4]
    json_write_path = f"{data_path}/json"


    with open(f"{schema_path}/{table}.json", 'r') as schema_json:
        schema = json.load(schema_json)

    os.makedirs(f"{json_write_path}/{data_size}", exist_ok=True)
    with open(f"{data_path}/{data_size}/{table}.dat", 'r', encoding="ISO-8859-1") as data_file:
        p = f"{json_write_path}/{data_size}/{table}.json"
        print(f"Creating... {p}")
        with open(p, 'w') as data_json_file:
            line = data_file.readline()
            while line:
                data_json_file.write(line_to_json(line, schema))
                line = data_file.readline()




