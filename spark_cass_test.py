from pyspark.sql import SparkSession
import os
import timeit
import shutil
from cassandra.cluster import Cluster, Session
import pandas as pd


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


if __name__ == "__main__":
    start = timeit.timeit()
    cat = 'store_sales'

    os.makedirs("tmp/", exist_ok=True)
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
    i = 1
    x = spark.createDataFrame(df)
    x.write.parquet(f"./tmp/{cat}_{i}.parquet", mode='overwrite')

    while ex.has_more_pages:
        ex.fetch_next_page()
        df: pd.DataFrame = ex._current_rows
        if df.shape[0] != 0:
            i += 1
            x = spark.createDataFrame(df, verifySchema=False)
            x.write.parquet(f"./tmp/{cat}_{i}.parquet", mode='overwrite')

    # print("Sum rows:", sum_rows)
    mergedDF = spark.read.option("mergeSchema", "true").parquet(f"tmp/{cat}*")
    mergedDF.createOrReplaceTempView(f"{cat}")
    sqlDF = spark.sql(f"SELECT count(*), sum('ss_net_profit') FROM {cat} GROUP BY 'ss_sold_date_sk'")
    sqlDF.show()
    sqlDF = spark.sql(f"SELECT * FROM {cat}")
    sqlDF.show()
    end = timeit.timeit()
    print(f"Czas {end - start}")

    shutil.rmtree("tmp", ignore_errors=True)
