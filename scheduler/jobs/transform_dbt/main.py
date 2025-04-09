from pathlib import Path

from config.base import log, os
from utils.common import load_settings_yaml
from utils.dbt import DBTRunner
from utils.job_scheduler import get_jobs_for_schedule, resolve_dependencies


def execute() -> None:
    """
    Handles the orchestration of dbt models based on the provided job name/config and schedule.
    Environment variables are used to get JOB_NAME and SCHEDULE.
    """
    dbt_runner = DBTRunner()

    job_name = os.getenv("JOB_NAME")
    schedule_name = os.getenv("SCHEDULE", "daily")

    if not job_name:
        log.error("JOB_NAME not set")
        raise ValueError("JOB_NAME not set")

    settings_path = Path(__file__).parent / "settings.yaml"
    config = load_settings_yaml(path=str(settings_path))

    all_jobs = get_jobs_for_schedule(config, schedule_name)
    ordered_jobs = resolve_dependencies(all_jobs, job_name)

    for job in ordered_jobs:
        job_config = job.get("config", {})
        dbt_config = dbt_runner.get_dbt_config_from_settings(job_config)
        log.info(f"Running dbt with config for job: {job['name']}")
        dbt_runner.run_dbt(dbt_config)


if __name__ == "__main__":
    """
    TODO: Remove this block when deploying to production
    Manually set environment variables for local testing.
    """
    os.environ["JOB_NAME"] = "refresh_facts"
    os.environ["SCHEDULE"] = "daily"

    execute()
