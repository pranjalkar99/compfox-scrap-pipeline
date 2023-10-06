import os
from google.cloud import storage

def upload_folder_to_gcs(bucket_name, folder_path):
    """Uploads all files from a folder to a Google Cloud Storage bucket."""
    # Initialize a client
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "compfox-367313-0c3890a157f2.json"
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Iterate through files in the folder
    for file_name in os.listdir(folder_path):
        # Check if the file is a JSON file
        if file_name.endswith('.json'):
            # Get the local file path
            local_file_path = os.path.join(folder_path, file_name)

            # Create a new blob (file) in the bucket
            blob = bucket.blob(file_name)

            # Upload the file
            blob.upload_from_filename(local_file_path)

            print(f"File {local_file_path} uploaded to {bucket_name}/{file_name}")

    return "succesfull upload to gcp"