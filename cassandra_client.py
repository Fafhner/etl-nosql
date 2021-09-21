from cassandra.cluster import Cluster
from timeit import default_timer as timer
from cassandra.query import SimpleStatement

def write_to(file_name, data, output_path=None, mode='w'):
    if output_path is not None:
        file_name = f"{output_path}/{file_name}"
    with open(file_name, mode) as cmd_file:
        cmd_file.write(data)


if __name__ == "__main__":
    cluster = Cluster(['192.168.55.16'])
    session = cluster.connect()

    tables = ["date_dim", "store_sales", "catalog_sales"]

    for i in range(200):
        dat_1 = timer()
        for table in tables:
            query = f"SELECT * FROM tpc_ds.{table}"
            statement = SimpleStatement(query, fetch_size=1000)

            ex = session.execute(statement, timeout=None)
            d = ex._current_rows
            while ex.has_more_pages:
                ex.fetch_next_page()
                d = ex._current_rows
        dat_2 = timer()

        write_to('result/TEST_CASS_2019_09_20', f"{dat_2-dat_1}", mode='a')

