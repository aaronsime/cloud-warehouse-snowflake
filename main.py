import os

from config.base import log, settings
from utils.common import get_execution_id
from utils.job_registry import JobRegistry


def main() -> None:
    """
    Main function that will run the job specified by the JOB_NAME environment variable.
    """
    registry = JobRegistry()
    job_name = os.getenv("JOB_NAME")

    if not job_name:
        raise ValueError("🚫 JOB_NAME environment variable not set")

    execution_id = get_execution_id()
    log.info(f"🧠 Available jobs: {list(registry.get_jobs().keys())}")
    log.info(f"🚀 Running job: {job_name} with execution ID: {execution_id}")

    job_function = registry.get_job(job_name)

    try:
        log_url = settings.LOG_URL_TEMPLATE.format(
            region=settings.REGION,
            project_id=settings.PROJECT_ID,
            execution_id=execution_id,
        )
        log.info(f"🔗 Logs: {log_url}")

        job_function()

        log.info(f"✅ Job '{job_name}' completed successfully")

    except Exception as e:
        log.error(f"💥 Job '{job_name}' failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
