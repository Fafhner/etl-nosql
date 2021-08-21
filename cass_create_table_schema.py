import yaml
import io
import json
import logging
import subprocess
import sys
from datetime import datetime

from util.grid import create_scenarios
from util import state

SCHEMA_STR = "CREATE TABLE {0}.{1} (\n{2},\n    PRIMARY KEY ({3}) );"

if __name__ == '__main__':
    tables_schema_path = "db/tables_schema"
    tables_schema = ["catalog_returns", "date_dim", "store_sales", "catalog_sales",
                            "web_sales", "warehouse", "customer", "customer_address", "store_returns"]
    tables_schema_dest = "db/cassandra/tables_schema"

    for table in tables_schema:
        with open(f"{tables_schema_path}/{table}.json", 'r') as schema_read:
            schema = json.load(schema_read)

        cass_schema = SCHEMA_STR.format(schema['namespace'],
                                        schema['table'],
                                        "\n".join([f"    {col['col_name']} {col['type']}" for col in schema['cols']]),
                                        schema['primary_key'])

        with open(f"{tables_schema_dest}/{table}.cqlsh", 'w') as schema_write:
            schema_write.write(cass_schema)


