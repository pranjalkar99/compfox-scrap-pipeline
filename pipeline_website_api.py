# main.py

from imports import *
from utils import *
from configs import *

@pipe.get("/")
async def root_message():
    return {"message": "Go to /docs for the API documentation."}

@pipe.get("/start-batch")
async def start_batch(limit_pdf: int = 10):
    os.makedirs('pdfs', exist_ok=True)
    count = 0
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    a_tags = soup.find_all('a')
    statuses = []
    for a in a_tags:
        
        try:
            if count <= limit_pdf:
                count+=1
                if a.get('href').endswith('.pdf'):
                    link =  "https://www.dir.ca.gov" +a.get('href')
                    download_pdf(link, "pdfs/"+a.get_text()+".pdf")
                    # print("Link:", link)
            # print("Text:", a.get_text())
            # print()
        except Exception as e:
            logging.warning("Unable to read -> " + a.get_text() + ": " + str(e))
    
    succes = make_batch('pdfs', 'temp_output')
    gcp_status = upload_folder_to_gcs(gcs_new_input_bucket,'temp_output/json_files')
    if succes and gcp_status:
        pdf_files = os.listdir("pdfs")
        for pdf_file in pdf_files:
            statuses.append({"pdf": pdf_file, "status": "Processed and uploaded"})
    else:
        statuses.append({"pdf": pdf_file, "status": "Batch Processing or uploading failed"})

    
    shutil.rmtree("pdfs")
    return {"message": "Batch started.", "statuses": statuses}

if __name__ == "__main__":
    uvicorn.run(pipe, port=8000)