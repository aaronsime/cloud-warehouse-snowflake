from typing import Dict

from google.cloud import bigquery

from config.base import settings


class BigQueryService:
    """
    Handles interactions with BigQuery for logging errors and AI summaries.
    """

    def __init__(self, parsed_log: Dict, ai_summary: str) -> None:
        self.client = bigquery.Client()
        self.project_id = settings.PROJECT_ID
        self.dataset_id = settings.DATASET_ERROR
        self.table_name = settings.TABLE_ERROR_SUMMARY
        self.timestamp = parsed_log["timestamp"]
        self.component = parsed_log["component"]
        self.resource_name = parsed_log["resource_name"]
        self.severity = parsed_log["severity"]
        self.error_message = parsed_log["error_message"]
        self.stack_trace = parsed_log["stack_trace"]
        self.ai_summary = ai_summary

    def log_to_bigquery(self) -> None:
        """
        Inserts error and AI summary into BigQuery.
        """

        table_id = f"{self.project_id}.{self.dataset_id}.{self.table_name}"
        row = {
            "timestamp": self.timestamp,
            "component": self.component,
            "resource_name": self.resource_name,
            "severity": self.severity,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "ai_summary": self.ai_summary,
        }

        self.client.insert_rows_json(table_id, [row])

    @staticmethod
    def table_schema() -> list[bigquery.SchemaField]:
        """
        Builds the schema for the BigQuery table.
        """

        return [
            bigquery.SchemaField("timestamp", "TIMESTAMP"),
            bigquery.SchemaField("component", "STRING"),
            bigquery.SchemaField("resource_name", "STRING"),
            bigquery.SchemaField("severity", "STRING"),
            bigquery.SchemaField("error_message", "STRING"),
            bigquery.SchemaField("stack_trace", "STRING"),
            bigquery.SchemaField("ai_summary", "STRING"),
        ]

    def create_table_if_not_exists(self) -> bool:
        """
        Creates the BigQuery table if it does not exist, using the exists_ok parameter.
        """
        full_table_id = f"{self.project_id}.{self.dataset_id}.{self.table_name}"
        table_ref = bigquery.TableReference.from_string(full_table_id)

        schema = self.table_schema()
        table = bigquery.Table(table_ref, schema=schema)

        self.client.create_table(table, exists_ok=True)
        return False

    def check_row_exists(self) -> bool:
        """
        Checks if a row with the same error_message already exists in the BigQuery table.
        """

        query = f"""
            SELECT COUNT(*) as count
            FROM `{settings.PROJECT_ID}.{settings.DATASET_ERRORS}.{settings.TABLE_ERROR_SUMMARY}`
            WHERE error_message = @error_message
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(
                    "error_message", "TIMESTAMP", self.error_message
                )
            ]
        )

        result = self.client.query(query, job_config=job_config).result()

        for row in result:
            return row["count"] > 0

        return False
