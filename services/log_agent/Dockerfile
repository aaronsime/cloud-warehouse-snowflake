FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install early to use cache
COPY services/log_agent/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the log_agent service code
COPY services/log_agent /app

# Copy shared config from root
COPY config /app/config

# Environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8080

EXPOSE 8080

# Start the Flask app
CMD ["python", "main.py"]
