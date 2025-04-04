# Use official slim Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . .

COPY scheduler/jobs/snowflake_ingestion/table_mappings.yaml /app/

# Make the entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Install dependencies from root-level requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=True
ENV JOB_NAME="snowflake_ingestion"
ENV PYTHONPATH="/app"

# Use custom entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
