import os
import pathlib
from pathlib import Path

from google.cloud import storage  # type: ignore
from ruamel.yaml import YAML


def load_table_mappings() -> dict:
    """Loads table mappings from a YAML file."""
    yaml = YAML(typ="safe")
    file_path = (
        pathlib.Path(__file__).resolve().parent.parent
        / "config"
        / "table_mappings.yaml"
    )
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.load(f)


def load_settings_yaml(path: str) -> dict:
    """Loads settings from a YAML file."""
    with open(path) as f:
        return YAML().load(f)


def get_execution_id() -> str:
    """Returns a unique identifier for the current execution."""
    return os.getenv("CLOUD_RUN_EXECUTION", "")


def upload_log_to_gcs(bucket_name: str, log_file_path: str, gcs_path: str) -> None:
    """
    Uploads a log file to a GCS bucket.
    """

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(log_file_path)


def combine_logs(main_log_path: str, dbt_log_path: str, output_path: str) -> None:
    """
    Combines orchestrator log and dbt.log into a single file.
    """
    with open(output_path, "w") as outfile:
        if Path(main_log_path).exists():
            outfile.write("===== Orchestrator Log =====\n")
            with open(main_log_path) as f:
                outfile.writelines(f)
            outfile.write("\n\n")

        if Path(dbt_log_path).exists():
            outfile.write("===== dbt.log =====\n")
            with open(dbt_log_path, encoding="utf-8", errors="replace") as f:
                outfile.writelines(f)
