import os
from llama_index import SimpleDirectoryReader, VectorStoreIndex, StorageContext,load_index_from_storage
from fastapi import FastAPI, Query
from dotenv import load_dotenv
app = FastAPI()
load_dotenv()#dotenv_path)
openai_key = os.getenv('OPENAI_KEY')

if openai_key is not None:
    os.environ['OPENAI_API_KEY'] = openai_key
else:
    # Handle the case when 'OPENAI_KEY' is not set
    print("OPENAI_KEY is not set. Please set the environment variable.")
index = None
index_dir = "./index"  # Make sure to set the correct index directory

def initialize_index(file_name):
    global index
    # storage_context = StorageContext.from_defaults()
    if os.path.exists(index_dir):
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context)
    #     index = load_index_from_storage(storage_context)
    else:
        documents = SimpleDirectoryReader(f"./documents/{file_name}").load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=index_dir)
        
# initialize_index()

def query_index(text: str):
    global index
    try:
        if text is None:
            return {"detail": "No text found, please include a ?text=blah parameter in the URL"}, 400

        query_engine = index.as_query_engine()
        response = query_engine.query(text)
        return {"response": str(response), "status": "success"}
    except Exception as e:
        return {"detail": str(e)}, 500


if __name__ == "__main__":
    initialize_index('Penner,  Jacob.pdf')
    print(query_index("what is the name of applicant and defendant"))