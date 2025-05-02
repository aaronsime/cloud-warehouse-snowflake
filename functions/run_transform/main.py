import base64
import json

from google.cloud import run_v2
from google.cloud.run_v2.types import RunJobRequest

from config.base import settings
from config.logging import configure_logging


def trigger_transformation_job(event: dict, context: None) -> None:
    """
    Triggered by a Pub/Sub message from the ingestion job.
    Starts a Cloud Run job for DBT transformation.
    """
    log = configure_logging()

    try:
        message = base64.b64decode(event["data"]).decode("utf-8")
        payload = json.loads(message)
        log.info(f"✅ Received Pub/Sub message for transformation trigger: {payload}")
    except Exception as e:
        log.error(f"❌ Failed to decode or parse Pub/Sub message: {e}")
        return

    if payload.get("status") != "ingestion_complete":
        log.warning(
            f"Message ignored: expected status 'ingestion_complete', got '{payload.get('status')}'"
        )
        return

    cloud_job_name = payload.get("cloud_job_name")
    if not cloud_job_name:
        log.error(
            "❌ 'job_name' missing in message payload. Cannot start transformation job."
        )
        return

    log.info(
        f"Preparing to trigger Cloud Run Job '{cloud_job_name}' in region '{settings.REGION}'..."
    )

    client = run_v2.JobsClient()
    full_job_name = f"projects/{settings.PROJECT_ID}/locations/{settings.REGION}/jobs/{cloud_job_name}"

    overrides = {
        "container_overrides": [
            {
                "env": [
                    {"name": "ENV", "value": settings.ENVIRONMENT},
                    {"name": "PROJECT_ID", "value": settings.PROJECT_ID},
                    {"name": "JOB_NAME", "value": payload.get("job_name", "")},
                    {"name": "SCHEDULE", "value": payload.get("schedule", "")},
                    {"name": "TRIGGER_SOURCE", "value": "post_ingestion"},
                ]
            }
        ]
    }

    request = RunJobRequest(name=full_job_name, overrides=overrides)

    try:
        response = client.run_job(request=request)
        log.info(
            f"Successfully triggered Cloud Run Job '{cloud_job_name}' "
            f"(operation: {response.name}) with env: ENV={settings.ENVIRONMENT}, "  # type: ignore[attr-defined]
            f"DATABASE={payload.get('database')}, SCHEMA={payload.get('schema')}, "
            f"SCHEDULE={payload.get('schedule')}"
        )

    except Exception as e:
        log.error(f"❌ Failed to start Cloud Run Job '{cloud_job_name}': {e}")
