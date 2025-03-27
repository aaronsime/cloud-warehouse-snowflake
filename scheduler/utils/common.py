import pathlib
from ruamel.yaml import YAML
import os

def load_table_mappings() -> dict:
    yaml = YAML(typ="safe")
    return yaml.load(pathlib.Path("table_mappings.yaml"))

def get_execution_id() -> str:
        """Returns a unique identifier for the current execution."""
        return os.getenv("CLOUD_RUN_EXECUTION", "")
