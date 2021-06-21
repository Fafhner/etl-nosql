#import modin.pandas as pd

from etl.pd_process import process_steps, get_steps


def cassandra_process(nodes, udf_file):
    from cassandra.cluster import Cluster, Session


    ret = process_steps(udf_file, nodes)

    return ret


def select_driver(driver):
    if driver == 'cassandra':
        return cassandra_process
    else:
        print(f"Error. Driver {driver} not found")
        return None

