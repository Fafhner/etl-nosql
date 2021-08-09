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
    return "{" + ", ".join(line_json) + "}\n"


if __name__ == '__main__':
    schema_path = '../../db/tables_schema'
    tables = ['catalog_returns', 'catalog_sales', 'customer', 'date_dim', 'store_sales', 'warehouse', 'web_sales']
    data_sizes = [1, 2, 3, 5]
    data_path = '../../db/table_data'
    json_write_path = '../../db/table_data/json'

    for data_size in data_sizes:
        for table in tables:
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




