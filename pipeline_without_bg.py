import os
import logging
import requests
import shutil
from bs4 import BeautifulSoup
from fastapi import FastAPI, BackgroundTasks
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

def clean_pdfs_folder():
    pdfs_folder = 'pdfs'
    for filename in os.listdir(pdfs_folder):
        file_path = os.path.join(pdfs_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error('Failed to delete %s. Reason: %s', file_path, e)


def clean_temp_output_folder():
    output_folder = 'temp_output'
    for item in os.listdir(output_folder):
        item_path = os.path.join(output_folder, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            logging.error('Failed to delete %s. Reason: %s', item_path, e)




statuses = []


def process_batch(limit_pdf: int = 10):
    try:
        clean_pdfs_folder()
        clean_temp_output_folder()
        import os

        # Get the current directory
        current_directory = os.getcwd()

        # List all files in the current directory
        files = os.listdir(current_directory)

        # Iterate through the files and remove .png files
        for file in files:
            if file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".html"):
                file_path = os.path.join(current_directory, file)
                os.remove(file_path)
                print(f"Removed: {file_path}")
    except Exception as e:
        logging.warning('Failed to clean file,', e)

    try: 
        os.makedirs('pdfs', exist_ok=True)
        count = 0
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')

        pdf_links_file = "pdf_links.txt"
        if os.path.exists(pdf_links_file):
            with open(pdf_links_file, 'r') as f:
                pdf_links = f.read().splitlines()
        else:
            pdf_links = []


        for table in tables:
            links = table.find_all('a', href=lambda href: (href and href.endswith('.pdf')))
            for link in links:
                if count >= limit_pdf:
                    break
                if link['href'] not in pdf_links:
                    pdf_links.append(link['href'])
                    with open(pdf_links_file, 'a') as f:
                        f.write(link['href'] + '\n')
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
            logging.info('Successfully processed these', statuses)



        return {"message": "Batch started.", "statuses": statuses}
    
    except Exception as e:
        logging.warning("MAJOR BATCH PROBLEM:----->",e)
        return {"message": "Some error occured, check logs."}


@pipe.get("/")
async def root_message():
    return {"message": "Go to /docs for the API documentation."}


@pipe.get("/start-batch")
async def startbatch(limit_pdf:int = 10):

    await process_batch(limit_pdf)
    logging.info("Batch started--> ")

    return {"message": "Batch processing has been scheduled."}


@pipe.get("/get-status")
async def get_batch_status():
    # You can return the statuses list as the current status of the batch processing/upload
    return {"statuses": statuses}

@pipe.get("/logs")
async def get_logs():
    with open('app.log', 'r') as log_file:
        logs = log_file.read()
    return {"logs": logs}


@pipe.get("/processed")
async def get_pdf_links():
    pdf_links_file = "pdf_links.txt"
    if os.path.exists(pdf_links_file):
        with open(pdf_links_file, 'r') as f:
            pdf_links = f.read().splitlines()
    else:
        pdf_links = []
    return {"pdf_links": pdf_links}