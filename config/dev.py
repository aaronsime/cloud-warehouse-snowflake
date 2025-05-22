from config.base import Settings


class DevSettings(Settings):

    PROJECT_ID: str = "dev-cloud-warehouse"
    ENVIRONMENT: str = "dev"
    GCS_BUCKET: str = "outbound-snowflake-dev/raw/incoming"
