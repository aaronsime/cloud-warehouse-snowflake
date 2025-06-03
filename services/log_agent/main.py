import base64
import json
from typing import Any, Dict, List, Optional, cast

from config.base import settings
from config.logging import configure_logging
from services.log_agent.clients.llm_client import AIResultTypedDict, GeminiClient
from services.log_agent.utils.bq_storage import BigQueryService
from services.log_agent.utils.dbt_log_parser import (
    DBTLogParser,
    DBTLogSummaryTypedDict,
    FailureDetailTypedDict,
)
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


def attempt_fetch_failing_rows_for_uniqueness_test(
    parsed_dbt_log: DBTLogSummaryTypedDict,
) -> Optional[List[Dict[str, Any]]]:
    """
    If a uniqueness-related test failure is found in parsed_dbt_log,
    this function attempts to query BigQuery for a sample of the failing rows.
    It processes only the first such failure found.
    """
    failure_data_sample: Optional[List[Dict[str, Any]]] = None
    detailed_failures: List[FailureDetailTypedDict] = parsed_dbt_log.get(
        "detailed_failure_info", []
    )

    for failure_detail in detailed_failures:
        if failure_detail.get("type") == "test_failure" and failure_detail.get(
            "is_uniqueness_related"
        ):
            test_node_name = failure_detail.get("test_node_name")
            if test_node_name:  # Ensure test_node_name is not None
                log.info(
                    f"Uniqueness-related test '{test_node_name}' failed. Attempting to fetch sample failing rows."
                )
                try:
                    query_bq_service = BigQueryService(parsed_log={}, ai_summary="")

                    test_failure_schema_from_settings: Optional[str] = None
                    if (
                        hasattr(settings, "DBT_TEST_FAILURE_SCHEMA")
                        and settings.DBT_TEST_FAILURE_SCHEMA
                    ):
                        test_failure_schema_from_settings = str(
                            settings.DBT_TEST_FAILURE_SCHEMA
                        )
                    else:
                        log.warning(
                            "settings.DBT_TEST_FAILURE_SCHEMA is not configured. "
                            "Cannot query test failure tables for test: %s",
                            test_node_name,
                        )
                        break

                    if test_failure_schema_from_settings:
                        failure_data_sample = (
                            query_bq_service.fetch_sample_failing_rows(
                                test_node_name=str(test_node_name),
                                test_failure_schema=test_failure_schema_from_settings,
                            )
                        )
                        if failure_data_sample:
                            log.info(
                                f"Fetched {len(failure_data_sample)} sample rows for test '{test_node_name}'."
                            )
                        else:
                            log.info(
                                f"No sample rows fetched for test '{test_node_name}'. Table might be empty, not exist, or query failed gracefully."
                            )
                except Exception as e_query:
                    log.error(
                        f"Error during attempt to query failing rows for test '{test_node_name}': {e_query}",
                        exc_info=True,
                    )

                break
    return failure_data_sample


def get_ai_summary_details(
    parsed_dbt_log: DBTLogSummaryTypedDict,
    orchestrator_context: Dict[str, Any],
    failure_data_sample: Optional[List[Dict[str, Any]]],
) -> AIResultTypedDict:
    """Gets AI summary, role, and score from GeminiClient."""
    log.info("Initializing Gemini Client for summarization.")
    gemini_client = GeminiClient(
        dbt_run_summary=cast(Dict[str, Any], parsed_dbt_log),
        orchestrator_context=orchestrator_context,
        failure_data_sample=failure_data_sample,
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

    failure_data_sample = attempt_fetch_failing_rows_for_uniqueness_test(
        parsed_dbt_log=parsed_dbt_log
    )

    ai_details: AIResultTypedDict = get_ai_summary_details(
        parsed_dbt_log=parsed_dbt_log,
        orchestrator_context=orchestrator_context,
        failure_data_sample=failure_data_sample,
    )
    ai_summary_text = ai_details["summary"]
    llm_role = ai_details["role"]
    llm_score = ai_details["score"]

    handle_bigquery_logging(
        parsed_dbt_log=parsed_dbt_log,
        ai_summary_text=ai_summary_text,
        llm_role=llm_role,
        llm_score=llm_score,
    )
    notify_on_slack(
        parsed_dbt_log=parsed_dbt_log,
        ai_summary_text=ai_summary_text,
        llm_role=llm_role,
        llm_score=llm_score,
    )

    return f"Processed: {blob_name}. Status: {parsed_dbt_log.get('status', 'UNKNOWN')} — AI summary sent."


if __name__ == "__main__":
    simple_payload_content = {
        "bucket": "dbt-logs-dev",
        "name": "logs/dbt/20250602-090703-transform-dbt.log",
    }
    encoded_payload = base64.b64encode(
        json.dumps(simple_payload_content).encode("utf-8")
    ).decode("utf-8")

    mock_event: dict = {"data": encoded_payload}

    print(f"Running local test for: {simple_payload_content.get('name')}")
    result = execute(event=mock_event, context=None)
    print(f"Local test finished. Result: {result}")
