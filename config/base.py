import logging
import os
from typing import Optional

from pydantic_settings import BaseSettings

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

    USER: str = "GCP_USER"
    PASSWORD: Optional[str] = os.getenv("SNOWFLAKE_PASSWORD")
    ACCOUNT: str = "QMUGLJO-NE36888"
    ROLE: str = "GCP_USER_ROLE"
    WAREHOUSE: str = "COMPUTE_WH"
    DATABASE: str
    SCHEMA: str = "RAW"
    REGION: str = "us-central1"
    PROJECT_ID: str
    DEFAULT_REGION: str = "us-central1"
    ENVIRONMENT: str

    PUBSUB_TOPIC: str = "cloud-scheduler-transform-topic"

    LOG_URL_TEMPLATE: str = (
        "https://console.cloud.google.com/run/jobs/executions/details/{region}/{execution_id}/logs?project={project_id}"
    )


settings = get_settings_class(os.environ.get("ENVIRONMENT") or "DEV")()
