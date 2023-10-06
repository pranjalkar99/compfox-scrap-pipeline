import os
import logging
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
# from pylogger import Logger  # This import is commented out because it's not used in the provided code
import pytest  # This import is commented out because it's not used in the provided code
from split import *  # This import is commented out because it's not used in the provided code
from upload_gcp import *  # This import is commented out because it's not used in the provided code

uri = "mongodb+srv://pw:pw@projects.wegmb8m.mongodb.net/?retryWrites=true&w=majority"
url = "https://www.dir.ca.gov/wcab/wcab-Decisions.htm"
uid_mongo_db = "pipeline_website"
pipe = FastAPI()
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s -  %(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')
client_name = "last_done"
collection_name = "compfox_simulate"
gcs_new_input_bucket = "compfox-pipeline-website-v2"


def download_pdf(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)
    return save_path


def get_mongo_db(collection_name, client_name, uri):
    client = MongoClient(uri)
    collection = client[client_name]
    db = collection[collection_name]
    return db


def mongosearch(file_name, uid_mongo_db):
    db = get_mongo_db(collection_name, client_name, uri)
    query = {
        "uid": uid_mongo_db,
        "last_done": {"$in": [file_name]}
    }
    return db.find(query)


@pipe.get("/")
async def root_message():
    return {"message": "Go to /docs for the API documentation."}


@pipe.get("/start-batch")
async def start_batch(limit_pdf: int = 10):
    os.makedirs('pdfs', exist_ok=True)
    count = 0
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    statuses = []
    pdf_links = []

    for table in tables:
        links = table.find_all('a', href=lambda href: (href and href.endswith('.pdf')))
        for link in links:
            if count >= limit_pdf:
                break
            if link['href'] not in pdf_links:
                pdf_links.append(link['href'])
                download_link = "https://www.dir.ca.gov" + link['href']
                download_pdf(download_link, "pdfs/" + link.get_text() + ".pdf")
                count += 1

        if count >= limit_pdf:
            break
    
    succes = make_batch('pdfs', 'temp_output')
    gcp_status = upload_folder_to_gcs(gcs_new_input_bucket,'temp_output/json_files')
    if succes and gcp_status:
        pdf_files = os.listdir("pdfs")
        for pdf_file in pdf_files:
            statuses.append({"pdf": pdf_file, "status": "Processed and uploaded"})
    else:
        statuses.append({"pdf": pdf_file, "status": "Batch Processing or uploading failed"})

    return {"message": "Batch started.", "statuses": statuses}