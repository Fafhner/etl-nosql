import json
import sys

SCHEMA_STR = "CREATE TABLE {0}.{1} (\n{2},\n    PRIMARY KEY ({3}) );"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("No arguments given.")
        exit(-1)

    with open(sys.argv[1]) as of:
        conf = json.load(of)['static']

    tables_schema_path = conf['tables_schema_path']
    tables_schema = conf['tables_schema']
    tables_schema_dest = conf['tables_schema_dest']

    for table in tables_schema:
        with open(f"{tables_schema_path}/{table}.json", 'r') as schema_read:
            schema = json.load(schema_read)
        
        pk = schema['primary_key'][0] if len(schema['primary_key']) == 1 else f"({','.join(schema['primary_key'])})"

        cass_schema = SCHEMA_STR.format(schema['namespace'],
                                        schema['table'],
                                        ",\n".join([f"    {col['col_name']} {col['type']}" for col in schema['cols']]),
                                        pk)

        with open(f"{tables_schema_dest}/{table}.cqlsh", 'w') as schema_write:
            schema_write.write(cass_schema)


