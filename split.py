import os
import tempfile
import aspose.words as aw
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader, PdfWriter
from fastapi import FastAPI, UploadFile
import json
import PyPDF2
import requests
import requests
import json
import uuid
import requests
from tqdm import tqdm
gcs_new_input_bucket="compfox-pipeline-cases"

## func for genrate the random id 
def random_id():
    return uuid.uuid4().hex[:16].upper()

## func for requesting the api to upload file
def upload_file(file_path, user_id):
    url = 'https://compfox-ai.onrender.com/upload'
    query_params = {
        'user_id': user_id
    }
    headers = {
        'accept': 'application/json'
    }
    files = {
        'file': (file_path, open(file_path, 'rb'), 'application/pdf')
    }

    response = requests.post(url, params=query_params, headers=headers, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f'Request failed with status code {response}'

def extract_text_from_pdf(file_path):
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    num_pages = pdf_reader.numPages
    text = ""
    for page in range(num_pages):
        page_obj = pdf_reader.getPage(page)
        text += page_obj.extractText()
    pdf_file_obj.close()
    return text




## asking the question from pdf
def ask_question(user_id, query):
    url = f'https://compfox-ai.onrender.com/askqa/{user_id}'
    query_params = {
        'query': query
    }
    headers = {
        'accept': 'application/json'
    }

    response = requests.post(url, params=query_params, headers=headers)
    
    if response.status_code == 200:
        res = response.json()
        return res['answer']
    else:
        return f'Request failed with status code {response}'
    

## Asking question until no error
def ask_until_question(user_id, query):
    count_try=0
    answer = ask_question(user_id, query)
    while "does not answer" or "no " in answer.lower() or count_try<3:
        count_try+=1
        print("Asking again", query)
        answer = ask_question(user_id, query)
    answer = "" if "doesn't know" in answer.lower() else answer
    return answer


## func to get the file name from file_path

def simple_filename(pathfile):
    return pathfile.split("/")[-1]

## func to make the json files
def make_batch(folder_path, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get all files in the source folder
    source_files = os.listdir(folder_path)

    for file_name in tqdm(source_files, desc="asking question to pdf for --> {file_name}"):
        # Check if the file is a PDF
        
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            file_ka_naam= file_name.split('.')[0]
            # Split the PDF into 5 pages
            id = random_id()
            response_data = upload_file(file_path, id)
            temp_dict = {}
            if 'successfully' in response_data['filename']:
                temp_dict['id'] = id
                temp_dict['applicant'] = ask_until_question(id, "what is the name of applicant")
                temp_dict['defendant'] = ask_until_question(id, "what is the name of defendant")
                temp_dict['date'] = ask_question(id, "date of case")
                temp_dict['case_number'] = ask_until_question(id, "what is the case number/adjucation number")
                temp_dict['district'] = ask_until_question(id, "write the name of the district office")
                temp_dict['decision'] = ask_until_question(id, "what is the final decision of the case")
                temp_dict['case_name'] = ask_until_question(id, "write the name of the case")
                temp_dict['section_codes'] = ask_until_question(id, "name the section codes in the case")
                temp_dict['references'] = ask_until_question(id, "name the references in the case")
                temp_dict['summary'] = ask_question(id, "write a small summary of the case")
                try:
                    temp_dict['text'] = extract_text_from_pdf(file_path)
                    temp_dict['seo_keywords'] = ask_question(id, "write 5 seo keywords for the case")
                except Exception:
                    temp_dict['text'] = ""
                    temp_dict['seo_keywords'] = ""
                temp_dict['gs_util'] = "gs://{}/{}".format(gcs_new_input_bucket, simple_filename(file_path))
            pdf = PdfReader(file_path)
            total_pages = len(pdf.pages)
            num_pages_per_file = min(total_pages, 5)
            num_files = (total_pages + num_pages_per_file - 1) // num_pages_per_file
            os.makedirs(output_folder+'/'+'json_files', exist_ok=True)
            os.makedirs(output_folder+'/'+file_ka_naam, exist_ok=True)
            path = os.path.join(output_folder,file_ka_naam)
            bda_html_list = []
            for i in tqdm(range(num_files),desc="spliting the pdf"):
                start_page = i * num_pages_per_file
                end_page = min(start_page + num_pages_per_file, total_pages)

                output_pdf = PdfWriter()
                for page in range(start_page, end_page):
                    output_pdf.add_page(pdf.pages[page])
                
                # Save the split PDF as a separate file
                output_file_path = os.path.join(path, f"{file_ka_naam}_split_{i + 1}.pdf")
                with open(output_file_path, "wb") as output_file:
                    output_pdf.write(output_file)
                doc = aw.Document(output_file_path)
                doc.save("h_output.html")

                with open("h_output.html", "r", encoding="utf8") as file:
                    soup = BeautifulSoup(file, 'html.parser').prettify()
                    html_list = soup.split("\n")

                cleaned_html = ""
                for line in tqdm(html_list ,desc="converting to html"):
                    if "Aspose" not in line and "<img" not in line:
                        cleaned_html += line
                bda_html_list.append(cleaned_html)
            temp_dict['filename'] = file_name
            temp_dict['html'] = bda_html_list
            json_data = json.dumps(temp_dict)
            # Save JSON data to a file
            path = os.path.join(output_folder,'json_files')
            with open(f"{path}/{file_ka_naam}.json", "w") as file:
                file.write(json_data)
    return "PDF split successful"
