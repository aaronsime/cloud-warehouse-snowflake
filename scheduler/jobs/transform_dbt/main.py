import base64
import json
from pathlib import Path

from config.base import log, os
from utils.common import load_settings_yaml
from utils.dbt import get_dbt_config_from_settings, run_dbt
from utils.job_scheduler import get_jobs_for_schedule, resolve_dependencies


def execute(event: dict, context: None) -> None:
    """
    Handles the orchestration of dbt models based on the provided job name/config and schedule.
    """
    payload = json.loads(base64.b64decode(event["data"]).decode("utf-8"))

    job_name = payload.get("job_name")
    schedule_name = payload.get("schedule", os.getenv("SCHEDULE", "daily"))

    if not job_name:
        log.error("JOB_NAME not set")
        raise ValueError("JOB_NAME not set")

    settings_path = Path(__file__).parent / "settings.yaml"
    config = load_settings_yaml(path=str(settings_path))

    all_jobs = get_jobs_for_schedule(config, schedule_name)
    ordered_jobs = resolve_dependencies(all_jobs, job_name)

    for job in ordered_jobs:
        job_config = job.get("config", {})
        dbt_config = get_dbt_config_from_settings(job_config)
        log.info(f"Running dbt with config for job: {job['name']}")
        run_dbt(dbt_config)


if __name__ == "__main__":

    """
    TODO: Remove this block when deploying to production
    """

    message = {"job_name": "refresh_facts", "schedule": "daily"}

    encoded_data = base64.b64encode(json.dumps(message).encode("utf-8")).decode("utf-8")

    raw_payload = {"data": encoded_data}

    execute(event=raw_payload, context=None)
