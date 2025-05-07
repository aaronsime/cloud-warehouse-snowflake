import importlib
import os
from pathlib import Path
from typing import Callable, Dict

from ruamel.yaml import YAML


class JobRegistry:
    def __init__(self, jobs_folder: str = "orchestrator.jobs") -> None:
        self.jobs_folder = jobs_folder
        self.jobs_dict: Dict[str, Callable[[], None]] = {}
        self.project_root = Path(__file__).resolve().parent.parent
        self.jobs_path_folder = self.project_root / "orchestrator" / "jobs"
        self.load_standard_jobs()
        self.load_transform_dbt_jobs()

    def load_standard_jobs(self) -> None:
        """Load standard jobs from the jobs folder."""
        for job_name in os.listdir(self.jobs_path_folder):
            job_dir = self.jobs_path_folder / job_name

            if job_dir.is_dir() and (job_dir / "main.py").exists():
                import_path = f"{self.jobs_folder}.{job_name}.main"
                job_module = importlib.import_module(import_path)
                self.jobs_dict[job_name] = job_module.execute

    def load_transform_dbt_jobs(self) -> None:
        """Load transform_dbt jobs from the settings.yaml file."""
        yaml_path = self.jobs_path_folder / "transform_dbt" / "settings.yaml"

        yaml = YAML(typ="safe")
        with open(yaml_path) as f:
            config = yaml.load(f)

        for job in config.get("schedule", {}).get("daily", []):
            job_name = job["name"]
            self.jobs_dict[job_name] = self.jobs_dict["transform_dbt"]

    def get_jobs(self) -> Dict[str, Callable[[], None]]:
        """Get all jobs in the registry."""
        return self.jobs_dict

    def get_job(self, job_name: str) -> Callable[[], None]:
        """Get a specific job by name."""
        return self.jobs_dict[job_name]
