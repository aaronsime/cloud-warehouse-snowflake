from snowflake.connector import connect, SnowflakeConnection

def snowflake_connection(user: str , password: str , account: str , role: str, warehouse: str, database: str, schema: str) -> SnowflakeConnection:
    conn = connect(
        user=user,
        password=password,
        account=account,
        role=role,
        warehouse=warehouse,
        database=database,
        schema=schema,
    )
    return conn



