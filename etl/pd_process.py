import json
import logging
from timeit import default_timer as timer

import cassandra
from cassandra.cluster import Session
from cassandra.query import SimpleStatement
import pandas as pd



def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def get_steps(file=None):
    if file is None:
        print("File is None")
        exit(-1)
    with open(file) as f:
        pushdown = json.load(f)

    return pushdown


def process_steps(cluster, udf: dict, spark):
    udf = udf.copy()

    dataframes = dict()
    step_time_info = {
        "data_acquisition_time": -1,
        "etl_processing_time": -1.,
        "overall_time": -1.
    }
    ov_time_start = timer()
    dat_aq_start = ov_time_start

    for df_val in udf['datasets'].values():

        file_inc = 0
        files = f"./tmp/{udf['name']}_{df_val['table_schema']}_{file_inc}.parquet"
        dataframes[f"{df_val['table_schema']}"] = f"./tmp/{udf['name']}_{df_val['table_schema']}*"

        session: Session = cluster.connect()
        session.row_factory = pandas_factory

        statement = SimpleStatement(df_val['query'], fetch_size=10000)

        try:
            ex = session.execute(statement, timeout=120)
        except cassandra.ReadFailure as err:
            logging.info(err.__str__())
            return None

        pdf: pd.DataFrame = ex._current_rows

        sdf = spark.createDataFrame(pdf)
        sdf.write.parquet(files, mode='overwrite')

        while ex.has_more_pages:
            ex.fetch_next_page()
            df: pd.DataFrame = ex._current_rows
            if df.shape[0] != 0:
                file_inc += 1
                files = f"./tmp/{udf['name']}_{df_val['table_schema']}_{file_inc}.parquet"
                dataframes[f"{df_val['table_schema']}"] = files
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


def process_to_hdfs(cluster, udf: dict, spark, cluster_size, data_size):
    udf = udf.copy()

    dataframes = dict()
    step_time_info = {
        "data_acquisition_time": -1,
    }
    ov_time_start = timer()
    dat_aq_start = ov_time_start

    for df_val in udf['datasets'].values():

        file_inc = 0
        files = f"./data/{cluster_size}/{data_size}/{udf['name']}/{df_val['table_schema']}/data_{file_inc}.parquet"
        dataframes[f"{df_val['table_schema']}"] = f"./data/{cluster_size}/{data_size}/{udf['name']}/{df_val['table_schema']}/data_*"

        session: Session = cluster.connect()
        session.row_factory = pandas_factory

        statement = SimpleStatement(df_val['query'], fetch_size=10000)

        try:
            ex = session.execute(statement, timeout=120)
        except cassandra.ReadFailure as err:
            logging.info(err.__str__())
            return None

        pdf: pd.DataFrame = ex._current_rows

        sdf = spark.createDataFrame(pdf)
        sdf.write.parquet(files, mode='overwrite')

        while ex.has_more_pages:
            ex.fetch_next_page()
            df: pd.DataFrame = ex._current_rows
            if df.shape[0] != 0:
                file_inc += 1
                files = f"./data/{cluster_size}/{data_size}/{udf['name']}/{df_val['table_schema']}/data_{file_inc}.parquet"
                dataframes[f"{df_val['table_schema']}"] = files
                sdf = spark.createDataFrame(df, verifySchema=False)
                sdf.write.parquet(files, mode='overwrite')
    dat_aq_end = timer()

    step_time_info['data_acquisition_time'] = dat_aq_end - dat_aq_start

    return step_time_info