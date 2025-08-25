# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Create output directory
RUN mkdir -p output

# Set environment variable for OpenAI
ENV OPENAI_API_KEY=your-key-here

# Entry point
CMD ["python", "verigpt_agent.py"]
