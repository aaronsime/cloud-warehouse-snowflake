import logging
import os


def configure_logging() -> logging.Logger:
    if os.environ.get("ENVIRONMENT", "dev").lower() == "dev":
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()

    return log
