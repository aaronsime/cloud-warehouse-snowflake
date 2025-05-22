from typing import Tuple

import functions_framework
from flask import Request
from google.cloud import run_v2

from config.base import settings
from config.logging import configure_logging


@functions_framework.http
def run(request: Request) -> Tuple[str, int]:
    """
    This cloud function allows users to manually trigger a Cloud Run job.
    See the README for required JSON structure.
    """
    log = configure_logging()

    try:
        request_json = request.get_json(silent=False)
        log.info(f"Received manual job trigger request: {request_json}")

        job_to_run = request_json["run_job_name"]
        overrides = request_json.get("overrides", {})
        region = request_json.get("region", settings.DEFAULT_REGION)

        log.info(
            f"Preparing to trigger Cloud Run job: '{job_to_run}' "
            f"in region: '{region}' with overrides: {list(overrides.keys()) or 'none'}"
        )

        client = run_v2.JobsClient()
        container_overrides = {
            "container_overrides": [
                {
                    "env": [
                        {"name": "ENV", "value": settings.ENVIRONMENT},
                        {"name": "PROJECT_ID", "value": settings.PROJECT_ID},
                    ]
                    + [{"name": k, "value": v} for k, v in overrides.items()],
                }
            ]
        }

        log.debug(f"Full container overrides: {container_overrides}")

        request = run_v2.RunJobRequest(
            name=f"projects/{settings.PROJECT_ID}/locations/{region}/jobs/{job_to_run}",
            overrides=container_overrides,
        )

        client.run_job(request=request)
        log.info(f"Successfully triggered job: '{job_to_run}' in region '{region}'")

        return "OK", 200

    except KeyError as e:
        log.error(f"Missing required key in request: {e}")
        return f"Missing required key: {e}", 400
    except Exception as e:
        log.exception(f"Failed to trigger job due to unexpected error: {e}")
        return "Internal Server Error", 500
