import os
import logging
import requests
import shutil, uvicorn

from fastapi import FastAPI, BackgroundTasks

from v2_pipeline.split import *
from v2_pipeline.upload_gcp import *
from v2_pipeline.process import *
from celery import Celery
from celery.result import AsyncResult

from dotenv import load_dotenv

dotenv_path = './.env'
load_dotenv()#dotenv_path)


# uri = os.getenv("uri")
# url = os.getenv("url")
# uid_mongo_db = os.getenv("uid_mongo_db")




statuses = []

pipe = FastAPI()
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s -  %(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')
# client_name = os.getenv('client_name')
# collection_name = os.getenv('collection_name')
# gcs_new_input_bucket = os.getenv('gcs_new_input_bucket')

# @pipe.on_event("startup")
# def on_startup():
#     celery.conf.update(pipe)







@pipe.get("/")
async def root_message():
    return {"message": "Go to /docs for the API documentation."}


@pipe.get("/start-batch")
def startbatch(limit_pdf: int = 10):
    # Call the Celery task asynchronously
    result = process_batch_full.apply_async(args=[limit_pdf])
    
    # Return the task_id
    return {"message": "Batch processing has been scheduled.", "task_id": result.id}

@pipe.get("/get-task-status/{task_id}")
def get_task_status(task_id: str):
    # Retrieve the task status using the task_id
    result = AsyncResult(task_id, app=celery)
    return {"status": result.status, "result": result.result}


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


if __name__ == "__main__":
    uvicorn.run(pipe, port=8000)