import os
import json


def create_schema(schema_json):
    properties = dict()

    for col in schema_json['cols']:
        mongo_type = ""
        if col['type'] == 'bigint':
            mongo_type = 'long'
        elif col['type'] in ['varchar', 'char', 'ascii']:
            mongo_type = 'string'
        else:
            mongo_type = col['type']
        properties[col['col_name']] = {"bsonType": mongo_type }

    options = {"validator": {"$jsonSchema": properties}}

    return f"db.createCollection(\"{schema_json['table']}\", {json.dumps(options, indent=2)})"


if __name__ == "__main__":
    schema_path = '../tables_schema'
    tables = ["catalog_returns", "date_dim", "store_sales", "catalog_sales",
              "web_sales", "warehouse", "customer", "customer_address", "store_returns"]
    data_sizes = [1, 3, 6, 9, 12]
    json_write_path = "tables_schema"

    for data_size in data_sizes:
        for table in tables:
            with open(f"{schema_path}/{table}.json", 'r') as schema_json:
                schema = json.load(schema_json)

            with open(f"{json_write_path}/{table}.mongo", 'w') as data_json_file:
                data_json_file.write(create_schema(schema))

