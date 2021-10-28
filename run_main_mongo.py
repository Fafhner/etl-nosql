import sys
from datetime import datetime

import db.mongodb.etl.etl_process as etl
from pyspark.sql import SparkSession
from pyarrow import fs
import uuid
from util.util import *



logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
print = rootLogger.info

py4j_logger = logging.getLogger('py4j')
py4j_logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

fileHandler = logging.FileHandler(f"spark_log_cass{datetime.now().strftime('%Y%m%d')}.output.log", mode='a')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

py4j_logger.addHandler(consoleHandler)
py4j_logger.addHandler(fileHandler)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No arguments given.")
        file = ""
        udf = ""
        loops = -1
        exit(-1)
    else:
        file = sys.argv[1]
        udf = sys.argv[2]
        loops = int(sys.argv[3])
        output = sys.argv[4]

    conf = load_from_json(file)

    udf = load_from_json(udf, conf['udf_path'])

    params = {
        "data": conf['scale'],
        "o_mem":  conf['cache_size'],
        "cluster_size": conf['cluster_size']
    }

    spark = SparkSession \
        .builder \
        .appName(f"Cassandra_experiments_{datetime.now().strftime('%Y%m%d')}") \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.0.0') \
        .getOrCreate()

    hdfs = fs.HadoopFileSystem('192.168.55.11', port=9000, user='magisterka')

    result_file = f"/home/magisterka/etl-nosql/result/run_etl_mongo.csv"

    data_tries = dict()
    idx = 0
    id_ = str(uuid.uuid4())
    udf['id'] = f"{str(datetime.now().date())}/{udf['name']}/{id_}"

    while idx < loops:
        udf['idx'] = idx
        try:
            result, result_df = etl.process(udf, spark, "mongodb://192.168.55.16")
            hdfs.delete_dir_contents("./tmp")
        except Exception as e:
            omit_udf = True
            logging.exception(e)
            break

        data_tries[idx] = result
        idx += 1
        a_data = f"{idx}," \
                 f"{id_}," \
                 f"{udf['name']}," \
                 f"{params['cluster_size']}," \
                 f"{params['data']}," \
                 f"{params['o_mem']}," \
                 f"{result['overall_time']}\n"
        write_to(result_file, a_data, mode='a')

