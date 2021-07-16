import cassandra as cass



from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
import pyspark




if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("CassTest") \
        .config("spark.cassandra.connection.host", "192.168.55.20") \
        .getOrCreate()

    sc = spark.sparkContext
    df = spark.read.format("org.apache.spark.sql.cassandra").options(table="warehouse", keyspace="tpc_ds").load()
    x = spark.sql("SELECT * FROM tpc_ds.warehouse")
    print(x)





