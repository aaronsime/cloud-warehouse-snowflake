import importlib
import os
from pathlib import Path
from typing import Callable, Dict

from ruamel.yaml import YAML

from config.logging import configure_logging


class JobRegistry:
    def __init__(self, jobs_folder: str = "scheduler.jobs") -> None:
        self.jobs_folder = jobs_folder
        self.jobs_dict: Dict[str, Callable[[], None]] = {}
        self.project_root = Path(__file__).resolve().parent.parent
        self.jobs_path_folder = self.project_root / "scheduler" / "jobs"
        self.log = configure_logging()

        if not self.jobs_path_folder.exists():
            raise FileNotFoundError(
                f"❌ Jobs folder not found: {self.jobs_path_folder}"
            )

        self.load_standard_jobs()
        self.load_transform_dbt_jobs()

    def load_standard_jobs(self) -> None:
        for job_name in os.listdir(self.jobs_path_folder):
            job_dir = self.jobs_path_folder / job_name

            if job_dir.is_dir() and (job_dir / "main.py").exists():
                import_path = f"{self.jobs_folder}.{job_name}.main"
                self.log.info(f"📦 Importing job module: {import_path}")
                job_module = importlib.import_module(import_path)

                if not hasattr(job_module, "execute"):
                    raise AttributeError(
                        f"❌ Job '{job_name}' must have an `execute()` function in main.py"
                    )

                self.jobs_dict[job_name] = job_module.execute

    def load_transform_dbt_jobs(self) -> None:
        yaml_path = self.jobs_path_folder / "transform_dbt" / "settings.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"❌ Missing settings.yaml: {yaml_path}")

        yaml = YAML(typ="safe")
        with open(yaml_path) as f:
            config = yaml.load(f)

        for job in config.get("schedule", {}).get("daily", []):
            job_name = job["name"]
            self.jobs_dict[job_name] = self.jobs_dict["transform_dbt"]
            self.log.info(f"🔗 Aliased job '{job_name}' to 'transform_dbt'")

    def get_jobs(self) -> Dict[str, Callable[[], None]]:
        return self.jobs_dict

    def get_job(self, job_name: str) -> Callable[[], None]:
        if job_name not in self.jobs_dict:
            raise ValueError(f"🚫 Job '{job_name}' not found in registry")
        return self.jobs_dict[job_name]
