# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy all code into the image
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r scheduler/requirements.txt

# Set default env (can be overridden at runtime)
ENV PYTHONUNBUFFERED=True
ENV JOB_NAME="example"

# Run the job dynamically via scheduler/main.py
CMD ["python", "scheduler/main.py"]
