import base64
import json

from cloudevents.http.event import CloudEvent
from functions_framework import cloud_event
from google.cloud import run_v2

from config.base import settings
from config.logging import configure_logging
from utils.common import load_settings_yaml


@cloud_event
def subscribe(cloud_event: CloudEvent) -> None:
    """
    Triggered by a Pub/Sub message, this function schedules one or more Cloud Run jobs
    based on the schedule specified in the incoming message.
    """

    log = configure_logging()
    settings_yml = load_settings_yaml("settings.yaml")

    try:
        message_str = base64.b64decode(cloud_event.data["message"]["data"]).decode(
            "utf-8"
        )
        log.info(f"Received Pub/Sub message payload: {message_str}")

        schedule = json.loads(message_str)
        schedule_name = schedule.get("schedule")

        if not schedule_name:
            log.error("⚠️ No 'schedule' field provided in the message payload.")
            return

        jobs_to_run = settings_yml["schedules"].get(schedule_name)
        if not jobs_to_run:
            log.warning(
                f"⚠️ No jobs found for schedule '{schedule_name}'. Check settings.yaml."
            )
            return

        log.info(
            f"Triggering {len(jobs_to_run)} job(s) for schedule: '{schedule_name}'"
        )

        client = run_v2.JobsClient()
        for job in jobs_to_run:
            job_display_name = job.get("name", "unknown")
            region = job.get("region", "unknown-region")
            run_job_name = job.get("run_job_name", "unknown-job")

            log.info(
                f"Preparing to start job: '{job_display_name}' in region: '{region}' (Cloud Run Job: '{run_job_name}')"
            )

            request = run_v2.RunJobRequest(
                name=f"projects/{settings.PROJECT_ID}/locations/{region}/jobs/{run_job_name}",
                overrides={
                    "container_overrides": [
                        {
                            "env": [
                                {"name": "ENV", "value": settings.ENVIRONMENT},
                                {"name": "PROJECT_ID", "value": settings.PROJECT_ID},
                                {"name": "JOB_NAME", "value": job_display_name},
                            ]
                        }
                    ]
                },
            )

            client.run_job(request=request)
            log.info(
                f"✅ Successfully triggered job '{job_display_name}' in region '{region}'"
            )

    except Exception as e:
        log.exception(f"❌ Failed to process schedule trigger. Error: {e}")
        raise
