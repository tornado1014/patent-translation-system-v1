# Use a stable Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for Pillow and PyArrow
# This is the key step to solve the build issues
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Define the command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]
