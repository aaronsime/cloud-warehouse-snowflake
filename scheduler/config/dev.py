from scheduler.config.base import Settings


class DevSettings(Settings):

    USER: str = "gcp_user"

    DATABASE: str = "DEV_CLOUD_DATAWAREHOUSE"
    PROJECT_ID: str = "dev-cloud-warehouse"
