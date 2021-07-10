import json

if __name__ == '__main__':
    tables_dest = "$HOME/etl-nosql/db/table_data"

    tables = ["date_dim", "store_sales", "catalog_sales", "web_sales", "warehouse", "customer"]
    sizes = [1, 5, 10, 15, 35, 50]

    infos = []
    for s in sizes:
        for t in tables:
            x = {
                "outputDir": "$HOME/etl-nosql/db/table_data/sstables",
                "outputDirName": f"{s}/{t}",
                "dataSrcPath": f"{tables_dest}/{s}/{t}.dat",
                "tableName": t
            }
            infos.append(x)

    with open('config.json', 'w') as outfile:
        json.dump({"infos": infos}, outfile, indent=4)
