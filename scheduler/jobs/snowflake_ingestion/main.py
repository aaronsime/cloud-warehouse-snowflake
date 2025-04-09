from config.base import log, settings
from connectors.snowflake import get_snowflake_connection
from utils.common import load_table_mappings
from utils.pubsub import publish_pubsub_message


def execute() -> None:
    """
    Ingests data from the raw stage in Snowflake into the target tables.
    """
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
    log.info(f"Session context: {cursor.fetchone()}")

    cursor.execute(
        f"""
        USE DATABASE {settings.DATABASE};
        USE SCHEMA {settings.SCHEMA};
        USE WAREHOUSE {settings.WAREHOUSE};
    """
    )
    log.info(
        f"Using database: {settings.DATABASE}, schema: {settings.SCHEMA}, warehouse: {settings.WAREHOUSE}"
    )

    mappings = load_table_mappings()
    for file_name, table_name in mappings["tables"].items():
        log.info(f"⏳ Loading {file_name} into {settings.SCHEMA}.{table_name}")
        copy_stmt = f"""
            COPY INTO "{settings.DATABASE}"."{settings.SCHEMA}"."{table_name}"
            FROM @DEV_CLOUD_DATAWAREHOUSE.RAW.RAW_STAGE/{file_name}
            FILE_FORMAT = (FORMAT_NAME = DEV_CLOUD_DATAWAREHOUSE.RAW.CSV_FORMAT)
            ON_ERROR = 'CONTINUE'
        """
        log.debug(f"Running COPY statement:\n{copy_stmt}")
        cursor.execute(copy_stmt)
        log.info(f"Loaded {file_name} into {settings.SCHEMA}.{table_name}")

    cursor.close()
    conn.close()

    message_id = publish_pubsub_message(
        topic=settings.PUBSUB_TOPIC,
        message={
            "status": "ingestion_complete",
            "database": settings.DATABASE,
            "schema": settings.SCHEMA,
            "job_name": "refresh_facts",
            "schedule": "daily",
        },
    )

    log.info(
        f"Published Pub/Sub message to {settings.PUBSUB_TOPIC}: message_id={message_id}"
    )


if __name__ == "__main__":
    execute()
