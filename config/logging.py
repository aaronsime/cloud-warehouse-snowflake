import logging
import os
from datetime import datetime


def configure_logging() -> logging.Logger:
    """Configures logging for the application. and log file is saved in /tmp/logs directory."""

    log_dir = "/tmp/logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    log_path = f"{log_dir}/dbt_job_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )

    # Save to env to access later
    os.environ["LOG_FILE_PATH"] = log_path
    log = logging.getLogger()

    return log
