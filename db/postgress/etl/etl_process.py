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
        spark.sql("CLEAR CACHE;")

        dataframes[f"{udf_val['table_schema']}"] = f"./tmp/{udf_val['table_schema']}*"
        df = spark.read.format("jdbc") \
            .option("query", udf_val['query']) \
            .load()

        df.write.parquet(f"tmp_psql/{udf_val['table_schema']}.parquet", mode='overwrite')
    dat_aq_end = timer()

    spark.sql("CLEAR CACHE;")

    for df_k in dataframes.keys():
        _ = spark.read.option("mergeSchema", "true").parquet(dataframes[df_k])

    etl_proc_start = timer()

    sqlDF = spark.sql(udf['spark_sql'])
    sqlDF.write.format("csv").save(f"postgres/output/{udf['id']}/{udf['idx']}.csv")

    etl_proc_end = timer()

    spark.sql("CLEAR CACHE;")

    ov_time_end = etl_proc_end

    step_time_info['data_acquisition_time'] = dat_aq_end - dat_aq_start
    step_time_info['etl_processing_time'] = etl_proc_end - etl_proc_start
    step_time_info['overall_time'] = ov_time_end - ov_time_start

    return step_time_info, sqlDF
