import json

if __name__ == '__main__':
    tables_dest = "../../db/table_data"

    tables = ["catalog_returns", "date_dim", "store_sales", "catalog_sales", "web_sales", "warehouse", "customer"]
    sizes = [2]

    infos = []
    for s in sizes:
        for t in tables:
            x = {
                "outputDir": "../../db/table_data/sstables",
                "outputDirName": f"{s}/tpc_ds/{t}",
                "dataSrcPath": f"{tables_dest}/{s}/{t}.dat",
                "tableName": t
            }
            infos.append(x)

    with open('config.json', 'w') as outfile:
        json.dump({"infos": infos}, outfile, indent=4)
