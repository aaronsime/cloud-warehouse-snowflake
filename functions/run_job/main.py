import base64
import json
import pathlib

from cloudevents.http.event import CloudEvent
from functions_framework import cloud_event
from google.cloud import logging, run_v2
from ruamel.yaml import YAML
from functions.config.base import settings, log



yaml = YAML(typ="safe")
SETTINGS = yaml.load(pathlib.Path("settings.yaml"))


@cloud_event
def subscribe(cloud_event: CloudEvent) -> None:
    """
    This function is triggered by a Pub/Sub message and starts the jobs
    """
    message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    log.info(f"Received message {message}")

    schedule = json.loads(message)
    log.info(f"Starting {schedule} jobs...")

    jobs_to_run = SETTINGS["schedules"][schedule["schedule"]]
    log.info(f"Starting {jobs_to_run} for {schedule['schedule']}")

    client = run_v2.JobsClient()
    for job in jobs_to_run:
            request = run_v2.RunJobRequest(
                name=f"projects/{settings.PROJECT_ID}/locations/{job['region']}/jobs/{job['run_job_name']}",
                overrides={
                    "container_overrides": [
                        {
                            "env": [
                                {"name": "ENV", "value": settings.ENVIRONMENT},
                                {"name": "PROJECT_ID", "value": settings.PROJECT_ID},
                            ]
                            + [{"name": "JOB_NAME", "value": job["name"]}]
                        }
                    ]
                },
            )

            client.run_job(request=request)
            log.info(f"{job['name']} job started.")
