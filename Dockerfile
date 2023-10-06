# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy everything in the current directory to the container
COPY . .

RUN pip install --upgrade pip

# Install the Python dependencies
RUN pip install -r requirements.txt

# Set the entrypoint command to run your FastAPI app
CMD ["uvicorn", "pipeline_website_api:app", "--host", "0.0.0.0","--port","8080"]
