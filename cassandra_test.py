import pandas as pd
from etl.etl_setup import cassandra_process
import json


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


if __name__ == "__main__":
    nodes = ['192.168.55.11']
    udf = "udf/10_intersect_1.json"

    stat = cassandra_process(nodes=nodes, udf_file=udf)

    with open("cassandra_test.result.json", 'w') as jf:
        json.dump(stat, jf)
