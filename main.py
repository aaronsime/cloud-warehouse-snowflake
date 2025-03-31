import os

from config.base import log, settings
from utils.common import get_execution_id
from utils.job_loader import get_jobs_dict


def main() -> None:
    """
    Main function that will run the job specified by the JOB_NAME environment variable.
    """
    jobs_dict = get_jobs_dict()
    log.info(f"🧠 Found jobs: {jobs_dict}")

    job_name = os.getenv("JOB_NAME")

    if not job_name:
        raise ValueError("🚫 JOB_NAME environment variable not set")

    execution_id = get_execution_id()
    log.info(f"🚀 Running job: {job_name} with execution ID: {execution_id}")

    if job_name not in jobs_dict:
        raise ValueError(f"🚫 Job '{job_name}' not found in jobs folder")

    job_function = jobs_dict[job_name]

    try:
        log_url = settings.LOG_URL_TEMPLATE.format(
            region=settings.REGION,
            project_id=settings.PROJECT_ID,
            execution_id=execution_id,
        )
        log.info(f"🔗 Logs: {log_url}")

        job_function()

    except Exception as e:
        log.error(f"💥 Job '{job_name}' failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
