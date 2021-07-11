import pandas
from distributed import Client, SSHCluster
import sys

cluster = SSHCluster(
    ["192.168.55.11", "192.168.55.12", "192.168.55.13", "192.168.55.14"],
    connect_options={"known_hosts": None, "client_username": sys.argv[1], "password": sys.argv[2]},
    scheduler_options={"port": 0, "dashboard_address": ":8797"}
)


client = Client(cluster)

import modin.pandas as pd

csvdata = pandas.read_csv("data2.csv")


def _r(xl: list):
    return pandas.DataFrame(xl, columns=csvdata.columns.values.tolist()).sort_values(by=['CRIM']).values.tolist()


data = client.scatter([csvdata.values.tolist()])
res = client.submit(_r, data).result()

print(res)