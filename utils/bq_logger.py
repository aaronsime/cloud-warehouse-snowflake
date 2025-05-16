from typing import Dict

from google.cloud import bigquery

from config.base import settings


def log_to_bigquery(parsed_log: Dict, ai_summary: str) -> None:
    """
    Inserts error and AI summary into BigQuery.
    """
    client = bigquery.Client()

    table_id = f"{settings.PROJECT_ID}.{settings.DATASET_ERRORS}.{settings.TABLE_ERROR_SUMMARY}"

    row = {
        "timestamp": parsed_log.get("timestamp"),
        "component": parsed_log.get("component"),
        "resource_name": parsed_log.get("resource_name"),
        "severity": parsed_log.get("severity"),
        "error_message": parsed_log.get("error_message"),
        "stack_trace": parsed_log.get("stack_trace"),
        "ai_summary": ai_summary,
    }

    client.insert_rows_json(table_id, [row])
