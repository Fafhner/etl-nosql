import json
from timeit import default_timer as timer

from cassandra.cluster import Session
from cassandra.query import SimpleStatement
import modin.pandas as pd


def delete_path(spark, path):
    sc = spark.sparkContext
    fs = (sc._jvm.org
          .apache.hadoop
          .fs.FileSystem
          .get(sc._jsc.hadoopConfiguration())
          )
    fs.delete(sc._jvm.org.apache.hadoop.fs.Path(path), True)



def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def get_steps(file=None):
    if file is None:
        print("File is None")
        exit(-1)
    with open(file) as f:
        pushdown = json.load(f)

    return pushdown


def process_steps(cluster, udf: dict, spark, tries: int):
    completed_tries = dict()
    udf = udf.copy()
    for try_ in range(tries):
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
            files = f"./tmp/{df_val['table_schema']}_{file_inc}.parquet"
            dataframes[f"{df_val['table_schema']}"] = files
            session: Session = cluster.connect()
            session.row_factory = pandas_factory
            statement = SimpleStatement(df_val['query'], fetch_size=5000)

            ex = session.execute(statement, timeout=120)
            df: pd.DataFrame = ex._current_rows


            sdf = spark.createDataFrame(df)
            sdf.write.parquet(files, mode='overwrite')

            while ex.has_more_pages:
                ex.fetch_next_page()
                df: pd.DataFrame = ex._current_rows
                if df.shape[0] != 0:
                    file_inc += 1
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

        completed_tries[try_] = udf


        delete_path(spark, "/tmp")

    return completed_tries
