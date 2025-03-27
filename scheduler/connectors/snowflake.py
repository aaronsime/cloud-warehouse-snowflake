import snowflake.connector


def get_snowflake_connection(
    user: str,
    password: str,
    account: str,
    warehouse: str,
    database: str,
    schema: str,
    role: str,
) -> snowflake.connector.connection:
    return snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema,
        role=role,
    )
