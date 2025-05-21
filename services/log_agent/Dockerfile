# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first for caching
COPY services/log_agent/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire log_agent source code
COPY services/log_agent /app

# Copy the shared config directory into the image
COPY config /app/config

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Expose the default port for Flask in Cloud Run
EXPOSE 8080

# Run the Flask app
CMD ["python", "utils/main.py"]
