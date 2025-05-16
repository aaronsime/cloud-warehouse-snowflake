import os

from pydantic_settings import BaseSettings


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

    DATASET: str = "raw"
    REGION: str = "us-central1"
    PROJECT_ID: str
    GCS_BUCKET: str
    ENVIRONMENT: str

    # TABLE_ERROR_SUMMARY: str
    # DATASET_ERROR: str

    PUBSUB_TOPIC: str = "cloud-orchestrator-transform-topic"

    LOG_URL_TEMPLATE: str = (
        "https://console.cloud.google.com/run/jobs/executions/details/{region}/{execution_id}/logs?project={project_id}"
    )

    # SLACK_WEBHOOK_URL: str


settings = get_settings_class(os.environ.get("ENVIRONMENT") or "DEV")()
