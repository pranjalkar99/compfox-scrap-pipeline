# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy everything in the current directory to the container
COPY . .

RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools
RUN sudo apt-get install libssl-dev


# Set the System.Globalization.Invariant flag (Note: This won't apply to Python)
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true
# Install the Python dependencies
RUN pip install -r requirements.txt

# Set the entrypoint command to run your FastAPI app
CMD ["uvicorn", "pipeline_without_bg:pipe", "--host", "0.0.0.0","--port","8080"]
