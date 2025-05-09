import os
import pathlib

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
