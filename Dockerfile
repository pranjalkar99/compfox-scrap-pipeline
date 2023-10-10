# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy everything in the current directory to the container
COPY . .

# Upgrade pip and install required packages
RUN pip install --upgrade pip setuptools && \
    apt-get update && apt-get install -y libssl-dev && \
    pip install -r requirements.txt

# Set the System.Globalization.Invariant flag (Note: This won't apply to Python)
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true

# Set the entrypoint command to run your FastAPI app
CMD ["uvicorn", "your_fastapi_app:pipe", "--host", "0.0.0.0", "--port", "8080"]
