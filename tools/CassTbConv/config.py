import json
import sys
if __name__ == '__main__':
    with open(sys.argv[1], 'r') as conf:
        config_file = json.load(conf)

    tables_data_src = config_file["tables_dest"]
    tables_schema_src = config_file["tables_schema_src"]
    outputDir = config_file["outputDir"]
    namespace = config_file["namespace"]
    out_file_name = config_file["out_file_name"]
    tables = config_file["tables"]
    sizes = config_file["sizes"]

    infos = []
    for s in sizes:
        for t in tables:
            x = {
                "outputDir": outputDir,
                "outputDirName": f"{s}/{namespace}/{t}",
                "dataSrcPath": f"{tables_data_src}/{s}/{t}.dat",
                "tableSchemaSrcPath": f"{tables_schema_src}/{t}.json",
                "tableName": t
            }
            infos.append(x)

    with open(out_file_name, 'w') as outfile:
        json.dump({"infos": infos}, outfile, indent=4)
