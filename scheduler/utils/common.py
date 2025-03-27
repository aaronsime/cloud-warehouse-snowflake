import pathlib
from ruamel.yaml import YAML

def load_table_mappings():
    yaml = YAML(typ="safe")
    return yaml.load(pathlib.Path("table_mappings.yaml"))