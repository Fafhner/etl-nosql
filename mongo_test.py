from timeit import default_timer as timer

from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("myApp") \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1') \
        .getOrCreate()

    t1 = timer()
    spark.read.format("com.mongodb.spark.sql.DefaultSource") \
        .option("uri", "mongodb://192.168.55.16/db.date_dim") \
        .load() \
        .write.parquet("tmp2/date_dim.parquet")
    spark.read.format("com.mongodb.spark.sql.DefaultSource") \
        .option("uri", "mongodb://192.168.55.16/db.store_sales") \
        .load() \
        .write.parquet("tmp2/store_sales.parquet")
    spark.read.format("com.mongodb.spark.sql.DefaultSource") \
        .option("uri", "mongodb://192.168.55.16/db.store_sales") \
        .load() \
        .write.parquet("tmp2/catalog_sales.parquet")
    t2 = timer()

    print(f"Time: {t2-t1}")