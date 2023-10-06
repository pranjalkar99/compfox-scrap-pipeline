from imports import *
from utils import *

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