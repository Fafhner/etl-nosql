from math import ceil
from timeit import default_timer as timer

import pymongo as pm
from pyspark.sql import SparkSession, Row
BATCH_SIZE = 100000


def process(client: pm.MongoClient, udf: dict, spark: SparkSession):
    udf = udf.copy()
    sc = spark.sparkContext

    dataframes = dict()
    step_time_info = {
        "data_acquisition_time": -1,
        "etl_processing_time": -1.,
        "overall_time": -1.
    }
    ov_time_start = timer()
    dat_aq_start = ov_time_start

    mongo_db = client['db']

    for udf_val in udf['datasets'].values():
        dataframes[f"{udf_val['table_schema']}"] = f"./tmp/{udf['name']}_{udf_val['table_schema']}*"
        file_inc = 0
        count_iter = 0

        collection = mongo_db[udf_val['table_schema']]
        count_docs = collection.count_documents(udf_val['filter'])
        iter_ = ceil(count_docs/BATCH_SIZE)

        while count_iter < iter_:
            d_start = BATCH_SIZE*count_iter
            d_stop = BATCH_SIZE*(count_iter+1)
            docs = collection.find(udf_val['filter'], udf_val['projection'], batch_size=BATCH_SIZE)[d_start:d_stop]
            df = sc.parallelize(list(docs)).map(lambda x: Row(**x)).toDF()
            files = f"./tmp/{udf['name']}_{udf_val['table_schema']}_{file_inc}.parquet"
            dataframes[f"{udf_val['table_schema']}"] = files
            df.write.parquet(files, mode='overwrite')
            file_inc += 1
            count_iter += 1

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

    return step_time_info
