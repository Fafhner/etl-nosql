import pymongo as pm

from pyspark import SparkConf

from util.grid import create_scenarios
import db.mongodb.etl.etl_process as etl
from util import state
import pymongo as pm
from pyspark.sql import SparkSession
import yaml
from pyarrow import fs
from timeit import default_timer as timer

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("myApp") \
        .getOrCreate()

    t1 = timer()
    spark.read.format("mongo") \
        .option("uri", "mongodb://192.168.55.16/db.date_dim") \
        .load() \
        .write.parquet("tmp2/date_dim.parquet")
    spark.read.format("mongo") \
        .option("uri", "mongodb://192.168.55.16/db.store_sales") \
        .load() \
        .write.parquet("tmp2/store_sales.parquet")
    spark.read.format("mongo") \
        .option("uri", "mongodb://192.168.55.16/db.store_sales") \
        .load() \
        .write.parquet("tmp2/catalog_sales.parquet")
    t2 = timer()

    print(f"Time: {t2-t1}")