from etl.pd_process import process_steps, process_to_hdfs


def cassandra_process(cluster, udf_file, spark):
    return process_steps(cluster, udf_file, spark)


def cassandra_to_hdfs(cluster, udf_file, spark, cluster_size, data_size):
    return process_to_hdfs(cluster, udf_file, spark, cluster_size, data_size)


def select_driver(driver):
    if driver == 'cassandra':
        return cassandra_process
    if driver == 'cassandra-hdfs':
        return cassandra_to_hdfs
    else:
        print(f"Error. Driver {driver} not found")
        return None



