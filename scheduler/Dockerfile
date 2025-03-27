FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r utils/requirements.txt

CMD ["python", "jobs/injest_data_snowflake/main.py"]
