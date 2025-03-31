import importlib
import os
from pathlib import Path

from config.base import log


def get_jobs_dict(jobs_folder: str = "scheduler.jobs") -> dict:
    """
    Enumerate all jobs in the scheduler/jobs folder and return a dictionary
    of job names and their execute functions.
    """
    jobs_dict = {}

    # Dynamically resolve the full path to scheduler/jobs
    project_root = Path(__file__).resolve().parent.parent  # /app
    jobs_path_folder = project_root / "scheduler" / "jobs"

    if not jobs_path_folder.exists():
        raise FileNotFoundError(f"❌ Jobs folder not found: {jobs_path_folder}")

    for job_name in os.listdir(jobs_path_folder):
        job_dir = jobs_path_folder / job_name

        if job_dir.is_dir() and (job_dir / "main.py").exists():
            import_path = f"{jobs_folder}.{job_name}.main"
            log.info(f"📦 Importing job module: {import_path}")

            job_module = importlib.import_module(import_path)

            if not hasattr(job_module, "execute"):
                raise AttributeError(
                    f"❌ Job '{job_name}' must have an `execute` function in main.py"
                )

            jobs_dict[job_name] = job_module.execute

    return jobs_dict
