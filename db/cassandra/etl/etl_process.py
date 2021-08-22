from timeit import default_timer as timer
from pyspark.sql import SparkSession


def process(udf: dict, spark: SparkSession):
    dataframes = dict()
    step_time_info = {
        "data_acquisition_time": -1,
        "etl_processing_time": -1.,
        "overall_time": -1.
    }
    ov_time_start = timer()
    dat_aq_start = ov_time_start

    for udf_val in udf['datasets'].values():
        dataframes[f"{udf_val['table_schema']}"] = f"./tmp/{udf_val['table_schema']}*"
        df = spark.read.format("org.apache.spark.sql.cassandra") \
            .option("spark.cassandra.connection.host", "192.168.55.20") \
            .option("spark.cassandra.connection.keepAliveMS", 1000) \
            .options(table=udf_val['table_schema'], keyspace="tpc_ds") \
            .load()

        df.createOrReplaceTempView(udf_val['table_schema'])
        spark.sql(udf_val['query']).write.parquet(f"tmp/{udf_val['table_schema']}.parquet", mode='overwrite')
        spark.sql(f"UNCACHE TABLE {udf_val['table_schema']}")
        df.unpersist()
    dat_aq_end = timer()


    for df_k in dataframes.keys():
        _ = spark.read.option("mergeSchema", "true").parquet(dataframes[df_k])
        _.createOrReplaceTempView(f"{df_k}")

    etl_proc_start = timer()

    sqlDF = spark.sql(udf['spark_sql'])
    sqlDF.show()
    etl_proc_end = timer()

    ov_time_end = etl_proc_end

    step_time_info['data_acquisition_time'] = dat_aq_end - dat_aq_start
    step_time_info['etl_processing_time'] = etl_proc_end - etl_proc_start
    step_time_info['overall_time'] = ov_time_end - ov_time_start

    return step_time_info, sqlDF
