# Use official slim Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install OS-level build tools (required by dbt + dependencies)
RUN apt-get update && apt-get install -y build-essential git

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install dbt-core dbt-snowflake

# Copy the entire project into the container
COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=true \
    PYTHONPATH=/app

# Use your simplified dynamic entrypoint
ENTRYPOINT ["./entrypoint.sh"]
