import json

file_names = ['catalog_returns',
              'customer',
              'catalog_sales',
              'date_dim',
              'store_sales',
              'warehouse',
              'web_sales']

files = dict()

for file_name in file_names:
    with open(file_name) as of:
        file_content = of.readlines()
        header = file_content[0].split(" ")
        namespace, table_name = header[2].split(".")
        primary_key = ""
        cols = []
        for i in range(1, len(file_content)):
            line_conent = file_content[i].strip().split()
            if len(line_conent) > 1 and line_conent[0] != ")":
                col, type = line_conent[0], line_conent[1]
                cols.append({"col_name": col, "type": type.split(',')[0]})
                if len(line_conent) > 2:
                    primary_key = col



        info = {"namespace": namespace, "table": table_name, "cols": cols,
                "primary_key": primary_key, "clustering_key": ""}

        with open(f'{file_name}.json', 'w') as wf:
            json.dump(info, wf, indent=2)
