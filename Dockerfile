# # Use the official Python image as a base
# FROM python:3.12-slim

# # Set the working directory in the container
# WORKDIR /app

# # Install dependencies first to improve cache behavior
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the application code into the container
# COPY . /app

# # Make port 80 available to the world outside this container
# EXPOSE 80

# # Start the FastAPI app with uvicorn
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]



# Use the official Python image as a base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first to improve cache behavior
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install mysqlclient for MySQL connection
RUN pip install mysqlclient

# Copy the application code into the container
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]