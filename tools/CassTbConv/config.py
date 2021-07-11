import json

if __name__ == '__main__':
    tables_dest = "../../db/table_data"

    tables = ["catalog_returns"]
    sizes = [1, 5, 10, 15, 35, 50]

    infos = []
    for s in sizes:
        for t in tables:
            x = {
                "outputDir": "../../db/table_data/sstables",
                "outputDirName": f"{s}/{t}.dat",
                "dataSrcPath": f"{tables_dest}/{s}/{t}.dat",
                "tableName": t
            }
            infos.append(x)

    with open('config.json', 'w') as outfile:
        json.dump({"infos": infos}, outfile, indent=4)
