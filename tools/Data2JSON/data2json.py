import os
import json


def line_to_json(line: str, schema):
    line_split = line.strip().split('|')

    schema_cols = schema['cols']
    line_json = dict()
    for i, split in enumerate(line_split):
        if split != '':
            col = schema_cols[i]
            if col['type'] in ['varchar', 'ascii', 'date']:
                line_json[col['col_name']] = f'"{split}"'
            else:
                line_json[col['col_name']] = f'{split}'


if __name__ == '__main__':
    schema_path = '$HOME/etl-nosql/db/table_schema'
    tables = ['catalog_returns', 'catalog_sales', 'customer', 'date_dim', 'store_sales', 'warehouse', 'web_sales']
    data_sizes = [1, 2, 3, 5]
    data_path = '$HOME/etl-nosql/db/table_data'
    json_write_path = '$HOME/etl-nosql/db/table_data/json'
    json_size = 1000

    os.makedirs(json_write_path)

    for table in tables:
        with open(f"{schema_path}/{table}.json") as schema_json:
            schema = json.load(schema_json)

        for data_size in data_sizes:
            os.makedirs(f"{json_write_path}/{data_size}")
            with open(f"{data_path}/{data_size}/{table}.dat") as data_file:
                line = data_file.readline()
                lines = []
                chunk_id = 0
                while line:
                    if len(lines) < json_size:
                        lines.append(line_to_json(line, schema))
                        line = data_file.readline()
                    else:
                        with open(f"{json_write_path}/{data_size}/{table}_{chunk_id}.json", 'w') as data_json_file:
                            json.dump({"data": lines}, data_json_file)
                        chunk_id += 1
                        lines = []
                with open(f"{json_write_path}/{data_size}/{table}.info.json", 'w') as data_json_file:
                    json.dump({"table": table, "chunks": chunk_id}, data_json_file)



