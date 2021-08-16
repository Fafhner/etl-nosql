from timeit import default_timer as timer

from pyarrow import fs
from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("myApp") \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1') \
        .getOrCreate()
    times = []
    hdfs = fs.HadoopFileSystem('192.168.55.11', port=9000, user='magisterka')
    hdfs.delete_dir('tmp2')
    for i in range(10):


        t1 = timer()
        spark.read.format("com.mongodb.spark.sql.DefaultSource") \
            .option("uri", "mongodb://192.168.55.20/db.catalog_sales") \
            .load() \
            .write.parquet(f"tmp2/catalog_sales.parquet")
        t2 = timer()
        times.append(t2-t1)
        hdfs.delete_dir('tmp2')

    print(f"*******************\nTime: \n{times}\n********************")