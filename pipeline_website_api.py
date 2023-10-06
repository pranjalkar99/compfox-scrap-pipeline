# main.py

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import uvicorn
# from pylogger import Logger
import logging
import shutil
import os
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://pw:pw@projects.wegmb8m.mongodb.net/?retryWrites=true&w=majority"
url = "https://www.dir.ca.gov/wcab/wcab-Decisions.htm"
# url = "https://www.dir.ca.gov/wcab/wcab-Decisions.htm"
uid_mongo_db = "pipeline_website"
pipe = FastAPI()
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s -  %(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')
client_name = "last_done"
collection_name = "compfox_simulate"
gcs_new_input_bucket="compfox-pipeline-website-v2"



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


import pytest
from split import *
from upload_gcp import *



pipe= FastAPI()

@pipe.get("/")
async def root_message():
    return {"message": "Go to /docs for the API documentation."}

@pipe.get("/start-batch")
async def start_batch(limit_pdf: int = 10):
    os.makedirs('pdfs', exist_ok=True)
    count = 0
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup)
    tables = soup.find_all('table')
    # a_tags = soup.find_all('a')
    statuses = []
    pdf_links = []
    for table in tables:
            # Find all <a> tags with href ending in .pdf within each table
            links = table.find_all('a', href=lambda href: (href and href.endswith('.pdf')))
            if count <= limit_pdf:
                count+=1
                for link in links:
                    if link not in pdf_links:
                        pdf_links.append(link['href'])
                        link =  "https://www.dir.ca.gov" +a.get('href')
                        download_pdf(link, "pdfs/"+a.get_text()+".pdf")
        
        # try:
        #     if count <= limit_pdf:
        #         count+=1
        #         if a.get('href').endswith('.pdf'):
        #             link =  "https://www.dir.ca.gov" +a.get('href')
        #             print(link)
        #             download_pdf(link, "pdfs/"+a.get_text()+".pdf")
        #             # print("Link:", link)
        #     # print("Text:", a.get_text())
        #     # print()
        # except Exception as e:
        #     logging.warning("Unable to read -> " + a.get_text() + ": " + str(e))
    
    # succes = make_batch('pdfs', 'temp_output')
    # gcp_status = upload_folder_to_gcs(gcs_new_input_bucket,'temp_output/json_files')
    # if succes and gcp_status:
    #     pdf_files = os.listdir("pdfs")
    #     for pdf_file in pdf_files:
    #         statuses.append({"pdf": pdf_file, "status": "Processed and uploaded"})
    # else:
    #     statuses.append({"pdf": pdf_file, "status": "Batch Processing or uploading failed"})

    
    # shutil.rmtree("pdfs")
    return {"message": "Batch started.", "statuses": statuses}



if __name__ == "__main__":
    uvicorn.run(pipe, port=8000)