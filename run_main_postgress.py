import sys
from datetime import datetime
from time import sleep
import db.postgress.etl.etl_process as etl
from pyspark.sql import SparkSession
from pyarrow import fs
import uuid
from util.util import *



logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)
print = rootLogger.info

py4j_logger = logging.getLogger('py4j')
py4j_logger.setLevel(logging.INFO)

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
        udfs = ""
        idx = -1
        exit(-1)
    else:
        file = sys.argv[1]
        udfs = sys.argv[2]
        idx = int(sys.argv[3])
        output = sys.argv[4]
    conf = load_from_json(file)

    udf = load_from_json(udfs, conf['udf_path'])

    params = {
        "data": conf['scale'],
        "o_mem":  conf['cache_size'],
        "cluster_size": conf['cluster_size']
    }

    spark = SparkSession \
        .builder \
        .appName(f"Postgres_experiments_{datetime.now().strftime('%Y%m%d')}") \
        .getOrCreate()

    hdfs = fs.HadoopFileSystem('192.168.55.11', port=9000, user='magisterka')

    sleep(10)
    data_tries = dict()
    id_ = str(uuid.uuid4())
    udf['id'] = f"{str(datetime.now().date())}/{udf['name']}/{id_}"

    udf['idx'] = idx
    try:
        result, result_df = etl.process(udf, spark)
        hdfs.delete_dir_contents("./tmp_psql")
    except Exception as e:
        omit_udf = True
        result = None
        logging.exception(e)
        exit(-1)

    data_tries[idx] = result
    idx += 1
    a_data = f"{idx}," \
             f"{id_}," \
             f"{udf['name']}," \
             f"{params['cluster_size']}," \
             f"{params['data']},{params['o_mem']}," \
             f"{result['overall_time']}\n"
    write_to(output, a_data, mode='a')

