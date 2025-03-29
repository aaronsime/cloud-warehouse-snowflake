import functions_framework
from flask import Request
from google.cloud import run_v2

from config.base import log, settings


@functions_framework.http
def run(request: Request) -> str:
    """
    Be aware of that only strings will be accepted as override variables.
    When boolean type needed, string of '0' or '1' should be used like below.
    {
        "run_job_name": "orca-scheduler-cloudrun-job-example",
        "region": "us-central1",
        "overrides": {
            "CAMPAIGN_CODE": "CTG-0001",
            "PRINT_MESSAGE": "0",
            "JOB_NAME": "example"
        }
    }
    """

    request_json = request.get_json(silent=False)
    log.info(f"Received request {request_json}")

    job_to_run, overrides, region = (
        request_json["run_job_name"],
        request_json.get("overrides", {}),
        request_json.get("region", settings.DEFAULT_REGION),
    )
    log.info(f"Starting {job_to_run} with override variables {overrides}")

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
    log.info(container_overrides)

    request = run_v2.RunJobRequest(
        name=f"projects/{settings.PROJECT_ID}/locations/{region}/jobs/{job_to_run}",
        overrides=container_overrides,
    )

    client.run_job(request=request)
    log.info(f"{job_to_run} job started.")

    return "OK"
