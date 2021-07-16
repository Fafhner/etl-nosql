import os

import cassandra as cass

from cassandra.cluster import Cluster, Session
import pandas as pd
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
import pyspark


def pandas_factory(colnames, rows):
    return  pd.DataFrame(rows, columns=colnames)



if __name__ == "__main__":
    os.makedirs("/tmp/warehouse")
    # spark = SparkSession \
    #     .builder \
    #     .appName("CassTest") \
    #     .getOrCreate()

    cluster = Cluster("192.168.55.16", connect_timeout=60)
    session: Session = cluster.connect()
    session.row_factory = pandas_factory

    statement = "SELECT * FROM tpc_ds.warehouse;"
    ex = session.execute(statement, timeout=120)
    df = ex._current_rows
    i = 0
    while ex.has_more_pages:
        ex.fetch_next_page()
        df.append(ex._current_rows).to_parquet(f"/tmp/warehouse{i}.parquet")
        i += 1

    # df = spark.read.format("org.apache.spark.sql.cassandra").options(table="catalog_sales", keyspace="tpc_ds").load()
    # x = spark.sql("SELECT count(*) FROM tpc_ds.warehouse")


    # os.rmdir(".tmp")






