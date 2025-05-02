import logging

from google.cloud import bigquery

from config.base import settings


def ingest_file(
    log: logging.Logger,
    file_name: str,
    table_name: str,
) -> None:
    """Ingests a file from GCS into BigQuery."""

    client = bigquery.Client()
    table_ref = f"{settings.PROJECT_ID}.{settings.DATASET}.{table_name}"
    gcs_uri = f"gs://{settings.GCS_BUCKET}/{file_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        autodetect=False,
    )

    log.debug(
        f"Submitting load job for file '{file_name}' into table '{table_ref}' from GCS URI '{gcs_uri}'"
    )

    load_job = client.load_table_from_uri(
        gcs_uri,
        table_ref,
        job_config=job_config,
    )
    load_job.result()

    log.info(
        f"✅ Successfully ingested '{file_name}' into '{settings.DATASET}.{table_name}'"
    )
