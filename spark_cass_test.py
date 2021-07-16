import os

import cassandra as cass
import shutil
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

    cat = 'store_sales'
    os.makedirs("tmp/warehouse", exist_ok=True)
    spark = SparkSession \
        .builder \
        .appName("CassTest") \
        .getOrCreate()

    cluster = Cluster(["192.168.55.16"], connect_timeout=20)
    session: Session = cluster.connect()
    session.row_factory = pandas_factory

    statement = f"SELECT * FROM tpc_ds.{cat};"
    ex = session.execute(statement, timeout=120)
    df: pd.DataFrame = ex._current_rows
    df['d_date'] = df['d_date'].astype('string')
    i = 1
    df.to_parquet(f"./tmp/{cat}{i}.parquet")
    sum_rows = df.count()

    while ex.has_more_pages:
        i += 1
        ex.fetch_next_page()
        df: pd.DataFrame = ex._current_rows
        df['d_date'] = df['d_date'].astype('string')
        df.to_parquet(f"./tmp/{cat}{i}.parquet")
        sum_rows += df.count()


    # df = spark.read.format("org.apache.spark.sql.cassandra").options(table="catalog_sales", keyspace="tpc_ds").load()
    # x = spark.sql("SELECT count(*) FROM tpc_ds.warehouse")




    print("Sum rows:", sum_rows)
    mergedDF = spark.read.option("mergeSchema", "true").parquet(f"tmp/{cat}*")
    mergedDF.createOrReplaceTempView(f"{cat}")
    sqlDF = spark.sql("SELECT count(*), sum('ss_net_profit') FROM people")
    sqlDF.show()

    shutil.rmtree("./tmp", ignore_errors=True)



