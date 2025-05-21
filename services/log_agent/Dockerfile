FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY services/log_agent/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full folder structure to preserve `services.*` imports
COPY services /app/services
COPY config /app/config

# Ensure Python sees /app as a package root
ENV PYTHONPATH=/app

CMD ["python", "services/log_agent/main.py"]
