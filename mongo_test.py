import pymongo as pm



if __name__ == "__main__":
    client = pm.MongoClient("192.168.55.20", 27017)
    db = client['db']
    date_dim_coll = db['date_dim']

    x = date_dim_coll.find({}, None, batch_size=10000)


    print(len(list(x[70000:90000])))