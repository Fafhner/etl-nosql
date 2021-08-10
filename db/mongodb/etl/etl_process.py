import json
from timeit import default_timer as timer

import pymongo as pm
import pandas as pd

BATCH_SIZE = 10000



def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def get_steps(file=None):
    if file is None:
        print("File is None")
        exit(-1)
    with open(file) as f:
        pushdown = json.load(f)

    return pushdown


def process_steps(client: pm.MongoClient, udf: dict, spark):
    udf = udf.copy()

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

        file_inc = 0
        files = f"./tmp/{udf['name']}_{udf_val['table_schema']}_{file_inc}.parquet"
        dataframes[f"{udf_val['table_schema']}"] = f"./tmp/{udf['name']}_{udf_val['table_schema']}*"

        collection = mongo_db[udf_val['table_schema']]
        count_docs = collection.count_documents(udf_val['filter'])
        documents = collection.find(udf_val['filter'], udf_val['projection'], batch_size=BATCH_SIZE)

        documents.


        pdf: pd.DataFrame = ex._current_rows

        sdf = spark.createDataFrame(pdf)
        sdf.write.parquet(files, mode='overwrite')

        while ex.has_more_pages:
            ex.fetch_next_page()
            df: pd.DataFrame = ex._current_rows
            if df.shape[0] != 0:
                file_inc += 1
                files = f"./tmp/{udf['name']}_{udf_val['table_schema']}_{file_inc}.parquet"
                dataframes[f"{udf_val['table_schema']}"] = files
                sdf = spark.createDataFrame(df, verifySchema=False)
                sdf.write.parquet(files, mode='overwrite')
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
