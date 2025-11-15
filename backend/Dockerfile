#
# REPLACE THIS FILE
# File: peptalk/backend/Dockerfile
#

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# --- UPDATED COMMAND ---
# 1. Run the scraper to get the 5 .md files.
# 2. Run the vector store to load all 5 .md files.
# 3. Run the API server.
CMD sh -c "python -m src.peptalk.data_ingestion && python -m src.peptalk.vector_store && uvicorn main:app --host 0.0.0.0 --port 8000"