from config.base import log
from connectors.snowflake import get_snowflake_connection
from utils.common import load_table_mappings


def execute() -> None:
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    mappings = load_table_mappings()
    for file_name, table_name in mappings["tables"].items():
        log.info(f"⏳ Loading {file_name} into RAW.{table_name}")
        copy_stmt = f"""
            COPY INTO RAW."{table_name}"
            FROM @RAW.RAW_STAGE/{file_name}
            FILE_FORMAT = (FORMAT_NAME = RAW.CSV_FORMAT)
            ON_ERROR = 'CONTINUE'
        """
        cursor.execute(copy_stmt)
        log.info(f"✅ Loaded {file_name} into RAW.{table_name}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    execute()
