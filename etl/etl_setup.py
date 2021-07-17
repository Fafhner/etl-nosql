import modin.pandas as pd

from etl.pd_process import process_steps, get_steps


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def cassandra_process(cluster, udf_file, spark, tries):
    ret = process_steps(cluster, udf_file, spark, tries)
    return ret


def select_driver(driver):
    if driver == 'cassandra':
        return cassandra_process
    else:
        print(f"Error. Driver {driver} not found")
        return None

