# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy everything in the current directory to the container
COPY . .
# Install libssl1.0.0 from a specific URL
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0.0_1.0.2n-1ubuntu5_amd64.deb
RUN dpkg -i libssl1.0.0_1.0.2n-1ubuntu5_amd64.deb

# Upgrade pip and install required packages
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

# Set the System.Globalization.Invariant flag (Note: This won't apply to Python)
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true

# Set the entrypoint command to run your FastAPI app
CMD ["uvicorn", "pipeline_without_bg:pipe", "--host", "0.0.0.0", "--port", "8080"]
