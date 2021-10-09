from timeit import default_timer as timer
from pyspark.sql import SparkSession


def process(udf: dict, spark: SparkSession, conn_uri):
    dataframes = dict()
    step_time_info = {
        "data_acquisition_time": -1,
        "etl_processing_time": -1.,
        "overall_time": -1.
    }

    spark.sql("CLEAR CACHE;")

    ov_time_start = timer()
    dat_aq_start = ov_time_start

    for udf_val in udf['datasets'].values():

        dataframes[f"{udf_val['table_schema']}"] = f"./tmp/{udf_val['table_schema']}*"
        df = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
            .option("uri", f"{conn_uri}/db.{udf_val['table_schema']}") \
            .load() \

        df.createOrReplaceTempView(udf_val['table_schema'])
        spark.sql(udf_val['query']).write.parquet(f"tmp/{udf_val['table_schema']}.parquet", mode='overwrite')
        df.unpersist()

    dat_aq_end = timer()
    spark.sql("CLEAR CACHE;")

    for df_k in dataframes.keys():
        _ = spark.read.option("mergeSchema", "true").parquet(dataframes[df_k])
        _.createOrReplaceTempView(f"{df_k}")

    etl_proc_start = timer()

    sqlDF = spark.sql(udf['spark_sql'])
    sqlDF.write.format("csv").save(f"mongo/output/{udf['id']}/output.csv")

    etl_proc_end = timer()
    ov_time_end = etl_proc_end

    spark.sql("CLEAR CACHE;")

    step_time_info['data_acquisition_time'] = dat_aq_end - dat_aq_start
    step_time_info['etl_processing_time'] = etl_proc_end - etl_proc_start
    step_time_info['overall_time'] = ov_time_end - ov_time_start

    return step_time_info, sqlDF
