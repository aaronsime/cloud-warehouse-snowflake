# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first for better layer caching
COPY services/log_agent/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire log_agent source code into /app
COPY services/log_agent /app

# Copy shared config (if used in your code)
COPY config /app/config

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8080

# Expose Flask port
EXPOSE 8080

# Start the Flask app
CMD ["python", "main.py"]
