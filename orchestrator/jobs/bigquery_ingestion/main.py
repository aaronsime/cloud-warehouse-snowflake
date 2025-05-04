from concurrent.futures import ThreadPoolExecutor, as_completed

from config.base import settings
from config.logging import configure_logging
from utils.common import load_table_mappings
from utils.injestion import ingest_file
from utils.pubsub import publish_pubsub_message


def execute() -> None:
    """
    Ingests data from the raw stage in GCS into the target tables in BigQuery.
    """
    log = configure_logging()
    log.info("Establishing connection to BigQuery...")

    log.info("Loading table mappings for ingestion...")
    mappings = load_table_mappings()
    tables = mappings.get("tables", {})

    log.info(f"Found {len(tables)} table(s) to ingest: {list(tables.values())}")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(ingest_file, log, file_name, table_name)
            for file_name, table_name in tables.items()
        ]
        for future in as_completed(futures):
            future.result()

    log.info("Publishing Pub/Sub message to notify job completion...")
    message_id = publish_pubsub_message(
        topic=settings.PUBSUB_TOPIC,
        message={
            "status": "ingestion_complete",
            "dataset": settings.DATASET,
            "project": settings.PROJECT_ID,
            "cloud_job_name": "cloud-scheduler-cloudrun-job-transform-dbt",
            "job_name": "refresh_facts",
            "schedule": "daily",
        },
    )

    log.info(
        f"Pub/Sub message published to topic '{settings.PUBSUB_TOPIC}' with message_id: {message_id}"
    )


if __name__ == "__main__":
    execute()
