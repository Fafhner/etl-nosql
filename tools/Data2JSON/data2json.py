import os
import json


def line_to_json(line: str, schema):
    line_split = line.strip().split('|')

    schema_cols = schema['cols']
    line_json = []
    for i, split in enumerate(line_split):
        if split != '':
            col_type = schema_cols[i]['type']
            col_name = schema_cols[i]['col_name']
            if col_type in ['varchar', 'ascii', 'date']:
                line_json.append(f'"{col_name}": "{split}"')
            else:
                line_json.append(f'"{col_name}": {split}')
    return "{" + ", ".join(line_json) + "}"


def dump_data(path, data):
    with open(path, 'w') as data_json_file:
        data_json_file.write("{" + f'"data": [{data}]' + "}")
        print(f"Created {p}")


if __name__ == '__main__':
    schema_path = '../../db/tables_schema'
    tables = ['catalog_returns', 'catalog_sales', 'customer', 'date_dim', 'store_sales', 'warehouse', 'web_sales']
    data_sizes = [1, 2, 3, 5]
    data_path = '../../db/table_data'
    json_write_path = '../../db/table_data/json'
    json_size = 2000

    os.makedirs(json_write_path, exist_ok=True)

    for data_size in data_sizes:
        for table in tables:
            with open(f"{schema_path}/{table}.json", 'r') as schema_json:
                schema = json.load(schema_json)

            os.makedirs(f"{json_write_path}/{data_size}/{table}", exist_ok=True)
            with open(f"{data_path}/{data_size}/{table}.dat", 'r', encoding="ISO-8859-1") as data_file:
                line = data_file.readline()
                lines = []
                chunk_id = 0

                while line or len(lines) > json_size:
                    if line is not None and len(lines) < json_size:
                        lines.append(line_to_json(line, schema))
                        line = data_file.readline()
                    else:
                        p = f"{json_write_path}/{data_size}/{table}/{table}_{chunk_id}.json"
                        dump_data(p, ",\n".join(lines))
                        chunk_id += 1
                        lines = []

                with open(f"{json_write_path}/{data_size}/{table}.info.json", 'w') as data_json_file:
                    json.dump({"table": table, "chunks": chunk_id}, data_json_file)