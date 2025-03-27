import importlib
import os

from scheduler.config.base import log


def get_jobs_dict(jobs_folder: str = "scheduler.jobs") -> dict:
    """
    Enumerate all jobs in the jobs folder and return a dictionary of job names and their execute functions.
    """
    jobs_dict = {}

    jobs_path_folder = os.path.join(os.path.dirname(__file__), "jobs")

    for job_name in os.listdir(jobs_path_folder):
        job_dir = os.path.join(jobs_path_folder, job_name)

        if os.path.isdir(job_dir) and os.path.exists(os.path.join(job_dir, "main.py")):
            import_path = f"{jobs_folder}.{job_name}.main"
            log.info(f"📦 Importing job module: {import_path}")

            job_module = importlib.import_module(import_path)

            if not hasattr(job_module, "execute"):
                raise AttributeError(
                    f"❌ Job '{job_name}' must have an `execute` function in main.py"
                )

            jobs_dict[job_name] = job_module.execute

    return jobs_dict
