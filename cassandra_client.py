from datetime import datetime
from cassandra.cluster import Cluster
from timeit import default_timer as timer
from cassandra.query import SimpleStatement
from pyspark.sql import SparkSession, DataFrame
from pyarrow import fs


def write_to(file_name, data, output_path=None, mode='w'):
    if output_path is not None:
        file_name = f"{output_path}/{file_name}"
    with open(file_name, mode) as cmd_file:
        cmd_file.write(data)


def spark_factory(colnames, rows):
    if len(rows) > 0:
        return spark.createDataFrame(rows, schema=colnames, verifySchema=False)
    else:
        return None


if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("Cassandra_experiments") \
        .getOrCreate()

    cluster = Cluster(['192.168.55.16'])
    hdfs = fs.HadoopFileSystem('192.168.55.11', port=9000, user='magisterka')

    tables = ["date_dim", "store_sales", "catalog_sales"]

    for i in range(200):
        session = cluster.connect()
        session.row_factory = spark_factory
        dat_1 = timer()

        for table in tables:
            query = f"SELECT * FROM tpc_ds.{table}"
            statement = SimpleStatement(query, fetch_size=1000)

            ex = session.execute(statement, timeout=None)
            d = ex._current_rows
            d.write.parquet('./temp/test', mode='append')
            while ex.has_more_pages:
                ex.fetch_next_page()
                d: DataFrame = ex._current_rows
                if d is not None and type(d) != 'list':
                    d.write.parquet('./temp/test', mode='append')
        dat_2 = timer()
        hdfs.delete_dir_contents("./tmp")
        write_to('result/TEST_CASS_2019_09_21', f"{datetime.now().strftime('%Y%m%d')},{dat_2-dat_1}", mode='a')

