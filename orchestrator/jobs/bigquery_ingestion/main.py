import time
import traceback
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
    start_time = time.time()
    log.info("Starting ingestion job...")

    log.info("Establishing connection to BigQuery...")

    log.info("Loading table mappings for ingestion...")
    mappings = load_table_mappings()
    tables = mappings.get("tables", {})

    log.info(f"Found {len(tables)} table(s) to ingest: {list(tables.values())}")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(ingest_file, file_name, table_name): (file_name, table_name)
            for file_name, table_name in tables.items()
        }

        log.info("Ingesting files into BigQuery...")

        for future in as_completed(futures):
            file_name, table_name = futures[future]
            try:
                future.result()
                log.info(f"✅ Ingested file '{file_name}' into table '{table_name}'")
            except Exception as e:
                log.error(
                    f"❌ Failed to ingest '{file_name}' → '{table_name}': {str(e)}"
                )
                log.debug(traceback.format_exc())

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

    total_time = time.time() - start_time
    log.info(f"Ingestion job completed in {total_time:.2f} seconds.")


if __name__ == "__main__":
    execute()
