from config.base import log, settings
from connectors.snowflake import get_snowflake_connection
from utils.common import load_table_mappings


def execute() -> None:
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    cursor.execute(f"USE DATABASE {settings.DATABASE}")
    cursor.execute(f"USE SCHEMA {settings.SCHEMA}")

    mappings = load_table_mappings()
    for file_name, table_name in mappings["tables"].items():
        log.info(f"⏳ Loading {file_name} into RAW.{table_name}")
        copy_stmt = f"""
            COPY INTO "{settings.DATABASE}"."{settings.SCHEMA}"."{table_name}"
            FROM @{settings.DATABASE}.{settings.SCHEMA}.RAW_STAGE/{file_name}
            FILE_FORMAT = (FORMAT_NAME = {settings.DATABASE}.{settings.SCHEMA}.CSV_FORMAT)
            ON_ERROR = 'CONTINUE'
        """
        cursor.execute(copy_stmt)
        log.info(f"✅ Loaded {file_name} into RAW.{table_name}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    execute()
