# Use official slim Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . .

# Make the entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Install dependencies from root-level requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=True
ENV JOB_NAME="example"
ENV PYTHONPATH="/app"

# Use custom entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
