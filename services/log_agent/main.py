import base64
import json
from typing import Any, Dict, Optional, cast

from config.logging import configure_logging
from services.log_agent.clients.llm_client import AIResultTypedDict, GeminiClient
from services.log_agent.utils.bq_storage import BigQueryService
from services.log_agent.utils.dbt_log_parser import DBTLogParser, DBTLogSummaryTypedDict
from services.log_agent.utils.slack_monitoring import SlackMessenger
from services.log_agent.utils.storage import load_log_from_gcs

log = configure_logging()


def get_event_payload(event: dict) -> Optional[Dict[str, Any]]:
    """Parses the Pub/Sub event data."""
    try:
        if not event or "data" not in event or event["data"] is None:
            log.error("Event data is missing or None.")
            return None
        payload_data = base64.b64decode(event["data"])
        payload_str = payload_data.decode("utf-8")
        payload = json.loads(payload_str)
        log.info("Pub/Sub event data parsed successfully.")
        return payload
    except Exception as e:
        log.error(f"Error parsing Pub/Sub event data: {e}", exc_info=True)
        return None


def fetch_log_content(bucket_name: str, blob_name: str) -> Optional[str]:
    """Fetches and decodes log content from GCS."""
    try:
        log_content_bytes = load_log_from_gcs(
            bucket_name=bucket_name, blob_name=blob_name
        )
        log_text: Optional[str] = None
        if isinstance(log_content_bytes, bytes):
            log_text = log_content_bytes.decode("utf-8")
        elif isinstance(log_content_bytes, str):
            log_text = log_content_bytes
        else:
            log.error(f"Unexpected content type from GCS: {type(log_content_bytes)}")
            return None
        log.info(
            f"Log content fetched successfully from gs://{bucket_name}/{blob_name}"
        )
        return log_text
    except Exception as e:
        log.error(
            f"Failed to load log from GCS: gs://{bucket_name}/{blob_name}. Error: {e}",
            exc_info=True,
        )
        return None


def get_ai_summary_details(
    parsed_dbt_log: DBTLogSummaryTypedDict, orchestrator_context: Dict[str, Any]
) -> AIResultTypedDict:
    """Gets AI summary, role, and score from GeminiClient."""
    log.info("Initializing Gemini Client for summarization.")
    gemini_client = GeminiClient(
        dbt_run_summary=cast(Dict[str, Any], parsed_dbt_log),
        orchestrator_context=orchestrator_context,
    )
    try:
        ai_result: AIResultTypedDict = gemini_client.summarise_best_role()
        log.info(
            f"AI Summary generated (Role: {ai_result['role']}, Score: {ai_result['score']}): {ai_result['summary'][:200]}..."
        )
        return ai_result
    except Exception as e:
        log.error(f"Error during AI summarization: {e}", exc_info=True)
        return AIResultTypedDict(
            summary=f"AI summary generation failed due to an error: {e}",
            role="error",
            score=0,
        )


def handle_bigquery_logging(
    parsed_dbt_log: DBTLogSummaryTypedDict,
    ai_summary_text: str,
    llm_role: str,
    llm_score: int,
) -> None:
    """Handles all BigQuery logging operations."""
    log.info("Initializing BigQueryService.")
    bq_service = BigQueryService(
        parsed_log=cast(Dict[str, Any], parsed_dbt_log),
        ai_summary=ai_summary_text,
        llm_role=llm_role,
        llm_score=llm_score,
    )
    try:
        table_created = bq_service.create_table_if_not_exists()
        if table_created:
            log.info(f"Created BigQuery table: {bq_service.full_table_id}")
        else:
            log.info(
                f"BigQuery table {bq_service.full_table_id} already exists or no action needed."
            )

        if not bq_service.check_row_exists():
            errors = bq_service.log_to_bigquery()
            if errors:
                log.error(f"BigQuery insert_rows_json reported errors: {errors}")
            else:
                log.info("Log summary inserted into BigQuery.")
        else:
            log.info(
                "Duplicate error signature found or check failed — skipping BigQuery insert."
            )
    except Exception as e:
        log.error(f"Error interacting with BigQuery: {e}", exc_info=True)


def notify_on_slack(
    parsed_dbt_log: DBTLogSummaryTypedDict,
    ai_summary_text: str,
    llm_role: str,
    llm_score: int,
) -> None:
    """Handles sending Slack notification."""
    log.info("Preparing Slack notification.")
    try:
        slack_messenger = SlackMessenger(
            parsed_log=cast(Dict[str, Any], parsed_dbt_log),
            ai_summary=ai_summary_text,
            llm_role=llm_role,
            llm_score=llm_score,
        )
        slack_messenger.send_slack_notification()
        log.info("Slack alert sent successfully.")
    except Exception as e:
        log.error(f"Error sending Slack notification: {e}", exc_info=True)


def execute(event: dict, context: Any) -> str:
    log.info("Received GCS trigger via Pub/Sub.")

    payload = get_event_payload(event)
    if not payload:
        return "Error: Could not parse Pub/Sub event data."

    bucket_name = payload.get("bucket")
    blob_name = payload.get("name")
    if not bucket_name or not blob_name:
        log.error("Error: Bucket name or blob name missing in payload.")
        return "Error: Bucket or blob name missing."

    if not blob_name.endswith(".log"):
        log.info(f"Skipping non-log file: {blob_name}")
        return "Ignored non-log file"

    log.info(f"Processing log file: {blob_name} in bucket: {bucket_name}")
    log_text = fetch_log_content(bucket_name, blob_name)
    if log_text is None:
        return f"Failed to load GCS log: gs://{bucket_name}/{blob_name}"

    parser = DBTLogParser(log_text.splitlines())
    parsed_dbt_log: DBTLogSummaryTypedDict = parser.parse()
    log.info(
        f"Log parsing complete. Status: {parsed_dbt_log.get('status')}, Should Save: {parsed_dbt_log.get('should_save_log')}"
    )

    if not parsed_dbt_log.get("should_save_log", False):
        log.info(
            "No significant warnings or errors found in dbt log. No further action."
        )
        return "Clean dbt run — no action taken"

    orchestrator_context: Dict[str, Any] = {
        "orchestrator_job_name": payload.get("attributes", {}).get(
            "orchestrator_job_name"
        ),
        "schedule": payload.get("attributes", {}).get("schedule"),
    }
    orchestrator_context = {
        k: v for k, v in orchestrator_context.items() if v is not None
    }

    ai_details: AIResultTypedDict = get_ai_summary_details(
        parsed_dbt_log, orchestrator_context
    )
    ai_summary_text = ai_details["summary"]
    llm_role = ai_details["role"]
    llm_score = ai_details["score"]

    handle_bigquery_logging(parsed_dbt_log, ai_summary_text, llm_role, llm_score)
    notify_on_slack(parsed_dbt_log, ai_summary_text, llm_role, llm_score)

    return f"Processed: {blob_name}. Status: {parsed_dbt_log.get('status', 'UNKNOWN')} — AI summary sent."


if __name__ == "__main__":
    simple_payload_content = {
        "bucket": "dbt-logs-dev",
        "name": "logs/dbt/20250525-094844-transform-dbt.log",
    }
    encoded_payload = base64.b64encode(
        json.dumps(simple_payload_content).encode("utf-8")
    ).decode("utf-8")

    mock_event: dict = {"data": encoded_payload}

    print(f"Running local test for: {simple_payload_content.get('name')}")
    result = execute(event=mock_event, context=None)
    print(f"Local test finished. Result: {result}")
