import logging
import os
from pymongo.mongo_client import MongoClient
from bs4 import BeautifulSoup
from v2_pipeline.llama import *
from v2_pipeline.upload_gcp import *
from v2_pipeline.split import *
from celery import Celery
from dotenv import load_dotenv
from v2_pipeline.celery_config import *
dotenv_path = './.env'
load_dotenv()#dotenv_path)


uri = os.getenv("uri")
url = os.getenv("url")
uid_mongo_db = os.getenv("uid_mongo_db")

logging.basicConfig(filename='app.log', filemode='w',level=logging.INFO, format='%(asctime)s -  %(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')
client_name = os.getenv('client_name')
collection_name = os.getenv('collection_name')
gcs_new_input_bucket = os.getenv('gcs_new_input_bucket')
url = os.getenv("url")

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
    pdfs_folder = 'documents'
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




@celery_task.task(bind=True)
def process_batch_full(self,limit_pdf: int = 10):
    import os
    try:

        limit_pdf = self.request.args.get("limit_pdf", limit_pdf)
        logging.warning('Starting batch processing')
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
        os.makedirs('documents', exist_ok=True)
        count = 0
        response = requests.get(url)

        logging.info('Response status code:', response.status_code)

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
                    download_pdf(download_link, "documents/" + link.get_text() + ".pdf")
                    count += 1

            if count >= limit_pdf:
                break

        succes = make_batch('documents', 'temp_output')
        gcp_status = upload_folder_to_gcs(gcs_new_input_bucket,'temp_output/json_files')
        if succes and gcp_status:
            pdf_files = os.listdir("documents")
            for pdf_file in pdf_files:
                statuses.append({"pdf": pdf_file, "status": "Processed and uploaded"})
        else:
            statuses.append({"pdf": pdf_file, "status": "Batch Processing or uploading failed"})
            logging.warning('Successfully processed these', statuses)



        return {"message": "Batch started.", "statuses": statuses}
    
    except Exception as e:
        logging.warning("MAJOR BATCH PROBLEM:----->",e)
        return {"message": "Some error occured, check logs."}


# def process_batch_full(limit_pdf: int = 10):
#     try:
#         logging.warning('Starting batch processing')
#         clean_pdfs_folder()
#         clean_temp_output_folder()
#         import os

#         # Get the current directory
#         current_directory = os.getcwd()

#         # List all files in the current directory
#         files = os.listdir(current_directory)

#         # Iterate through the files and remove .png files
#         for file in files:
#             if file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".html"):
#                 file_path = os.path.join(current_directory, file)
#                 os.remove(file_path)
#                 print(f"Removed: {file_path}")
#     except Exception as e:
#         logging.warning('Failed to clean file,', e)

#     try: 
#         os.makedirs('documents', exist_ok=True)
#         count = 0
#         response = requests.get(url)

#         logging.info('Response status code:', response.status_code)

#         soup = BeautifulSoup(response.content, 'html.parser')
#         tables = soup.find_all('table')

#         pdf_links_file = "pdf_links.txt"
#         if os.path.exists(pdf_links_file):
#             with open(pdf_links_file, 'r') as f:
#                 pdf_links = f.read().splitlines()
#         else:
#             pdf_links = []


#         for table in tables:
#             links = table.find_all('a', href=lambda href: (href and href.endswith('.pdf')))
#             for link in links:
#                 if count >= limit_pdf:
#                     break
#                 if link['href'] not in pdf_links:
#                     pdf_links.append(link['href'])
#                     with open(pdf_links_file, 'a') as f:
#                         f.write(link['href'] + '\n')
#                     download_link = "https://www.dir.ca.gov" + link['href']
#                     download_pdf(download_link, "documents/" + link.get_text() + ".pdf")
#                     count += 1

#             if count >= limit_pdf:
#                 break

#         succes = make_batch('documents', 'temp_output')
#         gcp_status = upload_folder_to_gcs(gcs_new_input_bucket,'temp_output/json_files')
#         if succes and gcp_status:
#             pdf_files = os.listdir("documents")
#             for pdf_file in pdf_files:
#                 statuses.append({"pdf": pdf_file, "status": "Processed and uploaded"})
#         else:
#             statuses.append({"pdf": pdf_file, "status": "Batch Processing or uploading failed"})
#             logging.info('Successfully processed these', statuses)



#         return {"message": "Batch started.", "statuses": statuses}
    
#     except Exception as e:
#         logging.warning("MAJOR BATCH PROBLEM:----->",e)
#         return {"message": "Some error occured, check logs."}

