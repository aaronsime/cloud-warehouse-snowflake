from snowflake.connector import SnowflakeConnection, connect

from scheduler.config.base import settings


def get_snowflake_connection() -> SnowflakeConnection:
    return connect(
        user=settings.USER,
        password=settings.PASSWORD,
        account=settings.ACCOUNT,
        warehouse=settings.WAREHOUSE,
        database=settings.DATABASE,
        schema=settings.SCHEMA,
        role=settings.ROLE,
    )
