# Use official slim Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install OS-level build tools (required by dbt + dependencies)
RUN apt-get update && apt-get install -y build-essential git

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install dbt + Snowflake adapter
RUN pip install dbt-core dbt-snowflake

# Copy the entire project
COPY . .

# Optional: copy any standalone config like a YAML mapping
COPY scheduler/jobs/snowflake_ingestion/table_mappings.yaml /app/
COPY scheduler/jobs/transform_dbt/settings.yaml /app/scheduler/jobs/transform_dbt/settings.yaml

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set env vars
ENV PYTHONUNBUFFERED=True
ENV JOB_NAME="snowflake_ingestion"
ENV PYTHONPATH="/app"

# Entrypoint for ingestion / transformation routing
ENTRYPOINT ["/app/entrypoint.sh"]
