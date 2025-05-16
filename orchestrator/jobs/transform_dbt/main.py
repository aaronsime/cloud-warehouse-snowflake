from pathlib import Path

from config.logging import configure_logging, os
from utils.common import load_settings_yaml
from utils.dbt_runner import DBTRunner
from utils.job_scheduler import DependencyResolver


def execute() -> None:
    """
    Handles the orchestration of dbt models based on the provided job name/config and schedule.
    Environment variables are used to get JOB_NAME and SCHEDULE.
    """
    log = configure_logging()

    log.info("Initializing DBT job runner...")
    resolver = DependencyResolver()
    dbt_runner = DBTRunner()

    job_name = os.getenv("JOB_NAME")
    schedule_name = os.getenv("SCHEDULE", "daily")

    log.info(f"Environment variables - JOB_NAME: {job_name}, SCHEDULE: {schedule_name}")

    if not job_name:
        log.error("JOB_NAME environment variable is not set. Cannot continue.")

    settings_path = Path(__file__).resolve().parent / "settings.yaml"

    log.info(f"Loading job settings from: {settings_path}")
    config = load_settings_yaml(path=str(settings_path))

    log.info(f"Resolving jobs for schedule: '{schedule_name}'")
    all_jobs = resolver.get_jobs_for_schedule(config, schedule_name)
    ordered_jobs = resolver.resolve_dependencies(all_jobs, str(job_name))

    log.info(
        f"Ordered execution list resolved: {[job['name'] for job in ordered_jobs]}"
    )

    for job in ordered_jobs:
        job_config = job.get("config", {})
        job_name = job.get("name", "unknown")
        log.info(f"Starting dbt run for job: '{job_name}' with config: {job_config}")

        dbt_config = dbt_runner.get_dbt_config_from_settings(job_config)
        dbt_runner.run_dbt(dbt_config)

        log.info(f"Completed dbt run for job: '{job_name}'")


if __name__ == "__main__":
    execute()
