from imports import *
from configs import *

def download_pdf(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)
    return save_path

def get_mongo_db(collection_name,client_name,uri):
    client = MongoClient(uri)
    collection = client[client_name]
    db = collection[collection_name]
    return db

def mongosearch(file_name,uid_mongo_db):
    db = get_mongo_db(collection_name, client_name, uri)
    query = {
        "uid": uid_mongo_db,
        "last_done": {"$in": [file_name]}
    }
    return db.find(query)