import modin.pandas as pd

from etl.pd_process import process_steps, get_steps


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def cassandra_process(nodes, udf_file):
    from cassandra.cluster import Cluster, Session

    cluster = Cluster(nodes)
    session: Session = cluster.connect()
    session.row_factory = pandas_factory
    session.default_fetch_size = None
    return process_steps(get_steps(udf_file), session)


def select_driver(driver):
    if driver == 'cassandra':
        return cassandra_process
    else:
        print(f"Error. Driver {driver} not found")
        return None

