FROM python:3.12-slim

WORKDIR /app

COPY services/log_agent/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY services /app/services
COPY config /app/config

ENV PYTHONPATH=/app

CMD ["python", "services/log_agent/main.py"]
