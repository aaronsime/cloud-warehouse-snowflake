from config.base import log, settings
from connectors.snowflake import get_snowflake_connection
from utils.common import load_table_mappings
from utils.pubsub import publish_pubsub_message


def execute() -> None:
    """
    Ingests data from the raw stage in Snowflake into the target tables.
    """
    log.info("📦 Establishing connection to Snowflake...")
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
    session_context = cursor.fetchone()
    log.info(f"🔐 Connected to Snowflake with session context: {session_context}")

    log.info(
        f"🧭 Switching to database: {settings.DATABASE}, schema: {settings.SCHEMA}, warehouse: {settings.WAREHOUSE}"
    )
    cursor.execute("SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
    log.info(f"🔐 Session context: {cursor.fetchone()}")

    log.info(f"🧭 Switching to database: {settings.DATABASE}")
    cursor.execute(f"USE DATABASE {settings.DATABASE}")

    log.info(f"🧭 Switching to schema: {settings.SCHEMA}")
    cursor.execute(f"USE SCHEMA {settings.SCHEMA}")

    log.info(f"🧭 Switching to warehouse: {settings.WAREHOUSE}")
    cursor.execute(f"USE WAREHOUSE {settings.WAREHOUSE}")

    log.info("🗂️ Loading table mappings for ingestion...")
    mappings = load_table_mappings()
    tables = mappings.get("tables", {})

    log.info(f"📄 Found {len(tables)} table(s) to ingest: {list(tables.values())}")

    for file_name, table_name in tables.items():
        log.info(
            f"⏳ Starting ingestion of file '{file_name}' into table '{settings.SCHEMA}.{table_name}'"
        )

        copy_stmt = f"""
            COPY INTO "{settings.DATABASE}"."{settings.SCHEMA}"."{table_name}"
            FROM @DEV_CLOUD_DATAWAREHOUSE.RAW.RAW_STAGE/{file_name}
            FILE_FORMAT = (FORMAT_NAME = DEV_CLOUD_DATAWAREHOUSE.RAW.CSV_FORMAT)
            ON_ERROR = 'CONTINUE'
        """

        log.debug(
            f"📥 Executing COPY statement for '{table_name}':\n{copy_stmt.strip()}"
        )
        cursor.execute(copy_stmt)

        log.info(
            f"✅ Successfully ingested '{file_name}' into '{settings.SCHEMA}.{table_name}'"
        )

    log.info("🔒 Closing Snowflake connection...")
    cursor.close()
    conn.close()

    log.info("📤 Publishing Pub/Sub message to notify job completion...")
    message_id = publish_pubsub_message(
        topic=settings.PUBSUB_TOPIC,
        message={
            "status": "ingestion_complete",
            "database": settings.DATABASE,
            "schema": settings.SCHEMA,
            "cloud_job_name": "cloud-scheduler-cloudrun-job-transform-dbt",
            "job_name": "refresh_facts",
            "schedule": "daily",
        },
    )

    log.info(
        f"📨 Pub/Sub message published to topic '{settings.PUBSUB_TOPIC}' with message_id: {message_id}"
    )


if __name__ == "__main__":
    execute()
