import logging
import os
from typing import Optional

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

    USER: str
    PASSWORD: Optional[str] = os.getenv("SNOWFLAKE_PASSWORD")
    ACCOUNT: str = "ne36888"
    ROLE: Optional[str] = os.getenv("SNOWFLAKE_ROLE")
    WAREHOUSE: Optional[str] = os.getenv("SNOWFLAKE_WAREHOUSE")
    DATABASE: str
    SCHEMA: str = "RAW"
    REGION: str = "us-central1"
    PROJECT_ID: str
    DEFAULT_REGION: str = "us-central1"
    ENVIRONMENT: str

    LOG_URL_TEMPLATE: str = (
        "https://console.cloud.google.com/run/jobs/executions/details/{region}/{execution_id}/logs?project={project_id}"
    )


settings = get_settings_class(os.environ.get("ENVIRONMENT") or "DEV")()
