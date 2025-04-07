import subprocess

from config.base import log


def get_dbt_config_from_settings(settings: dict) -> dict:
    """
    Extracts dbt configuration from the settings dictionary.
    :param settings:
    :return:
    """
    return {
        "command": settings.get("DBT_COMMAND", "run"),
        "target": settings.get("DBT_TARGET", "dev"),
        "models": settings.get("DBT_MODELS"),
        "vars": settings.get("DBT_VARS"),
        "full_refresh": str(settings.get("DBT_FULL_REFRESH", "false")).lower()
        == "true",
    }


def run_dbt(config: dict) -> None:
    """
    Runs the dbt command with the provided configuration.
    :param config:
    :return:
    """
    cmd = [
        "dbt",
        config["command"],
        "--profiles-dir",
        ".",
        "--target",
        config["target"],
    ]

    if config.get("models"):
        cmd += ["--select", config["models"]]
    if config.get("full_refresh"):
        cmd.append("--full-refresh")
    if config.get("vars"):
        cmd += ["--vars", config["vars"]]

    log.info(f"Running dbt command: {' '.join(cmd)}")

    subprocess.run(["dbt", "deps", "--profiles-dir", "."], check=True)
    subprocess.run(cmd, check=True)
