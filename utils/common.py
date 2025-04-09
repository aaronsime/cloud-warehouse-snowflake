import os
import pathlib
from typing import Any

from ruamel.yaml import YAML


def load_table_mappings() -> dict:
    """Loads table mappings from a YAML file."""
    yaml = YAML(typ="safe")
    return yaml.load(pathlib.Path("table_mappings.yaml"))


def load_settings(path: str) -> dict[str, Any]:
    yaml = YAML(typ="safe")
    return yaml.load(pathlib.Path(path))


def load_settings_yaml(path: str) -> dict:
    """Loads settings from a YAML file."""
    with open(path) as f:
        return YAML().load(f)


def get_execution_id() -> str:
    """Returns a unique identifier for the current execution."""
    return os.getenv("CLOUD_RUN_EXECUTION", "")
