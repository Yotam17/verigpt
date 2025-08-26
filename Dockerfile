# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Create output directory
RUN mkdir -p output

# Don't set environment variables here - they will be loaded from .env file
# The .env file should be mounted or copied at runtime
# The application uses python-dotenv to load environment variables

# Expose port for FastAPI
EXPOSE 8000

# Entry point for FastAPI service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
