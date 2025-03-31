from config.base import log, settings
from connectors.snowflake import get_snowflake_connection
from utils.common import load_table_mappings


def execute() -> None:
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
    log.info(f"🔍 Session context: {cursor.fetchone()}")

    cursor.execute(f"USE DATABASE {settings.DATABASE}")
    log.info(f"🔍 Using database: {settings.DATABASE}")
    cursor.execute(f"USE SCHEMA {settings.SCHEMA}")
    log.info(f"🔍 Using schema: {settings.SCHEMA}")

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
        log.info(f"✅ Loaded {file_name} into {settings.SCHEMA}.{table_name}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    execute()
