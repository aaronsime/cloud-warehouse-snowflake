import subprocess
from pathlib import Path

from config.logging import configure_logging


class DBTRunner:
    def __init__(self) -> None:
        self.dbt_project_dir = Path(__file__).resolve().parents[1] / "snow_wh"
        self.log = configure_logging()

    @staticmethod
    def get_dbt_config_from_settings(settings: dict) -> dict:
        """
        Extracts dbt configuration from the settings dictionary.
        """
        return {
            "command": settings.get("DBT_COMMAND", "run"),
            "target": settings.get("DBT_TARGET", "dev"),
            "models": settings.get("DBT_MODELS"),
            "vars": settings.get("DBT_VARS"),
            "full_refresh": str(settings.get("DBT_FULL_REFRESH", "false")).lower()
            == "true",
        }

    def run_dbt(self, config: dict) -> None:
        """
        Runs the dbt command with the provided configuration.
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

        self.log.info(f"Running dbt command: {' '.join(cmd)}")

        subprocess.run(
            ["dbt", "deps", "--profiles-dir", "."], cwd=self.dbt_project_dir, check=True
        )
        subprocess.run(cmd, cwd=self.dbt_project_dir, check=True)
