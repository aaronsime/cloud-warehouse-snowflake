from datetime import datetime
from pathlib import Path

from config.base import settings
from config.logging import configure_logging, os
from utils.common import combine_logs, load_settings_yaml, upload_log_to_gcs
from utils.dbt_runner import DBTRunner
from utils.job_scheduler import DependencyResolver


def execute() -> None:
    """
    Handles the orchestration of dbt models based on the provided job name/config and schedule.
    facilitates the execution of dbt runs by resolving dependencies by using the DependencyResolver
    to interpret the job configuration and schedule from the settings.yaml file
    and passes the resolved jobs to the DBTRunner for execution.
    """
    log = configure_logging()
    log.info("Initializing DBT job runner...")

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    gcs_path = f"logs/dbt/{timestamp}-transform-dbt.log"
    log_path = os.environ.get("LOG_FILE_PATH")
    combined_path = f"/tmp/combined_{timestamp}.log"

    try:
        resolver = DependencyResolver()
        dbt_runner = DBTRunner()

        job_name = os.getenv("JOB_NAME")
        schedule_name = os.getenv("SCHEDULE", "daily")

        log.info(
            f"Environment variables - JOB_NAME: {job_name}, SCHEDULE: {schedule_name}"
        )

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
            log.info(
                f"Starting dbt run for job: '{job_name}' with config: {job_config}"
            )

            dbt_config = dbt_runner.get_dbt_config_from_settings(job_config)
            dbt_runner.run_dbt(dbt_config)

            log.info(f"Completed dbt run for job: '{job_name}'")

    finally:

        log.info("Combining logs...")
        dbt_log_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "snow_wh"
            / "logs"
            / "dbt.log"
        )
        if log_path is not None:
            combine_logs(
                main_log_path=log_path,
                dbt_log_path=str(dbt_log_path),
                output_path=combined_path,
            )
        log.info(f"Log files combined successfully combined path is {combined_path}.")

        if log_path and Path(log_path).exists():
            upload_log_to_gcs(
                bucket_name=settings.GCS_LOG_BUCKET,
                log_file_path=combined_path,
                gcs_path=gcs_path,
            )
            log.info(
                f"Uploaded log file to GCS: gs://{settings.GCS_LOG_BUCKET}/{gcs_path}"
            )
        else:
            log.info("Log file not found — skipping GCS upload.")


if __name__ == "__main__":
    # os.environ["JOB_NAME"] = "refresh_facts"
    # os.environ["SCHEDULE"] = "daily"

    execute()
