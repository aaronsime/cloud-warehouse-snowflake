import logging
import os

from pydantic_settings import BaseSettings

# Set up logging
if os.environ.get("ENVIRONMENT", "dev").lower() == "dev":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def get_settings_class(environment_name: str):  # type: ignore
    """
    Selects a Settings Class to use based on the environment variable
    `ENVIRONMENT`.
    """
    # importing in-class to avoid circular dependency.
    from .dev import DevSettings


    return {
        "dev": DevSettings,
    }[environment_name.lower()]


class Settings(BaseSettings):

    USER: str = os.getenv("SNOWFLAKE_USER"),
    PASSWORD: str = os.getenv("SNOWFLAKE_PASSWORD"),
    ACCOUNT: str = os.getenv("SNOWFLAKE_ACCOUNT"),
    ROLE: str = os.getenv("SNOWFLAKE_ROLE"),
    WAREHOUSE: str = os.getenv("SNOWFLAKE_WAREHOUSE"),
    DATABASE: str
    SCHEMA: str ="RAW"


settings = get_settings_class(os.environ.get("ENVIRONMENT") or "DEV")()