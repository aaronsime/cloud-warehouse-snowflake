from config.base import log, os
from utils.common import load_settings_yaml
from utils.dbt import get_dbt_config_from_settings, run_dbt
from utils.job_scheduler import get_jobs_for_schedule, resolve_dependencies


def execute() -> None:
    """
    Handles the orchestration of dbt models based on the provided job name/config and schedule.
    """
    job_name = os.getenv("JOB_NAME")
    schedule_name = os.getenv("SCHEDULE", "daily")

    if not job_name:
        log.error("JOB_NAME not set")
        raise ValueError("JOB_NAME not set")

    config = load_settings_yaml(path="settings.yaml")
    all_jobs = get_jobs_for_schedule(config, schedule_name)
    ordered_jobs = resolve_dependencies(all_jobs, job_name)

    for job in ordered_jobs:
        job_config = job.get("config", {})
        dbt_config = get_dbt_config_from_settings(job_config)
        log.info(f"Running dbt with config for job: {job['name']}")
        run_dbt(dbt_config)


if __name__ == "__main__":
    execute()
