from config.base import Settings


class DevSettings(Settings):

    DATABASE: str = "DEV_CLOUD_DATAWAREHOUSE"
    PROJECT_ID: str = "dev-cloud-warehouse"
    ENVIRONMENT: str = "dev"
    GCS_BUCKET: str = "outbound-snowflake-dev/raw/incoming"
