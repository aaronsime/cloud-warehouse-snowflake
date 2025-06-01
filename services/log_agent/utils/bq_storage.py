from typing import Any, Dict, List, Optional

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from config.base import settings


class BigQueryService:
    """
    Handles interactions with BigQuery for logging parsed dbt errors and AI summaries.
    Errors from BigQuery API calls will propagate up to the caller.
    Logging of this class's operations should be handled by the calling module (e.g., main.py).
    """

    client: bigquery.Client
    project_id: str
    dataset_id: str
    table_name: str
    full_table_id: str

    timestamp: Optional[str]
    component: str
    resource_name: str
    severity: str
    primary_error_message: Optional[str]
    detailed_error_info: Optional[str]
    dbt_version: Optional[str]
    dbt_invocation_command: Optional[str]
    dbt_target: Optional[str]
    dbt_failing_nodes: Optional[str]
    dbt_final_summary_stats: Optional[str]
    error_log_snippet: Optional[str]
    ai_summary: str
    llm_role: str
    llm_score: int

    @staticmethod
    def format_timestamp_for_bq(raw_timestamp_input: Optional[Any]) -> Optional[str]:
        """
        Formats a raw timestamp string (or other type) for BigQuery compatibility.
        - Replaces comma with period for fractional seconds.
        - Replaces 'T' separator with space.
        - Truncates fractional seconds to 6 digits.
        - Returns None if input is None, or attempts string conversion for other types.
        """
        if isinstance(raw_timestamp_input, str):
            formatted_timestamp = raw_timestamp_input.replace(",", ".").replace(
                "T", " "
            )
            parts = formatted_timestamp.split(".")
            if len(parts) == 2:
                date_time_part = parts[0]
                fractional_part = parts[1]
                if len(fractional_part) > 6:
                    fractional_part = fractional_part[:6]
                return f"{date_time_part}.{fractional_part}"
            else:
                return formatted_timestamp
        elif raw_timestamp_input is None:
            return None
        else:
            return str(raw_timestamp_input)

    def __init__(
        self,
        parsed_log: Dict[str, Any],
        ai_summary: str,
        llm_role: Optional[str] = None,
        llm_score: Optional[int] = None,
    ) -> None:
        self.client = bigquery.Client(project=settings.PROJECT_ID)
        self.project_id = settings.PROJECT_ID
        self.dataset_id = settings.DATASET_ERROR
        self.table_name = settings.TABLE_ERROR_SUMMARY
        self.full_table_id = f"{self.project_id}.{self.dataset_id}.{self.table_name}"

        self.timestamp = BigQueryService.format_timestamp_for_bq(
            parsed_log.get("parsed_timestamp")
        )

        self.component = str(parsed_log.get("component", "unknown_component"))
        self.resource_name = str(parsed_log.get("resource_name", "unknown_resource"))
        self.severity = str(parsed_log.get("severity", "UNKNOWN"))

        self.primary_error_message = parsed_log.get("primary_error_message")
        self.detailed_error_info = parsed_log.get("full_error_details")

        self.dbt_version = parsed_log.get("dbt_version")
        self.dbt_invocation_command = parsed_log.get("invocation_command")

        dbt_target_profile = parsed_log.get("target_profile")
        dbt_target_name = parsed_log.get("target_name")
        if dbt_target_profile and dbt_target_name:
            self.dbt_target = f"{dbt_target_profile}/{dbt_target_name}"
        elif dbt_target_name:
            self.dbt_target = str(dbt_target_name)
        else:
            self.dbt_target = None

        failing_nodes_list = parsed_log.get("failing_nodes", [])
        self.dbt_failing_nodes = (
            ", ".join(failing_nodes_list) if failing_nodes_list else None
        )

        self.dbt_final_summary_stats = parsed_log.get("final_summary_line")
        error_log_snippet_list = parsed_log.get("error_log_snippet", [])
        self.error_log_snippet = (
            "\n".join(error_log_snippet_list) if error_log_snippet_list else None
        )

        self.ai_summary = ai_summary
        self.llm_role = str(
            llm_role if llm_role is not None else parsed_log.get("role", "unknown")
        )
        self.llm_score = int(
            llm_score if llm_score is not None else parsed_log.get("score", 0)
        )

    def log_to_bigquery(self) -> List[Dict[str, Any]]:
        """
        Inserts error details, parsed log context, and AI summary into BigQuery.
        Returns the list of errors from insert_rows_json (empty if successful).
        Raises exceptions from BQ client on critical failure.
        """
        row_to_insert: Dict[str, Any] = {
            "timestamp": self.timestamp,
            "component": self.component,
            "resource_name": self.resource_name,
            "severity": self.severity,
            "primary_error_message": self.primary_error_message,
            "detailed_error_info": self.detailed_error_info,
            "dbt_version": self.dbt_version,
            "dbt_invocation_command": self.dbt_invocation_command,
            "dbt_target": self.dbt_target,
            "dbt_failing_nodes": self.dbt_failing_nodes,
            "dbt_final_summary_stats": self.dbt_final_summary_stats,
            "error_log_snippet": self.error_log_snippet,
            "ai_summary": self.ai_summary,
            "llm_role": self.llm_role,
            "llm_score": self.llm_score,
        }

        errors = self.client.insert_rows_json(self.full_table_id, [row_to_insert])
        return list(errors)

    @staticmethod
    def table_schema() -> List[bigquery.SchemaField]:
        """
        Defines the schema for the BigQuery table storing error summaries.
        """
        return [
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("component", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("resource_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("severity", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("primary_error_message", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("detailed_error_info", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("dbt_version", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("dbt_invocation_command", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("dbt_target", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("dbt_failing_nodes", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("dbt_final_summary_stats", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("error_log_snippet", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("ai_summary", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("llm_role", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("llm_score", "INTEGER", mode="NULLABLE"),
        ]

    def create_table_if_not_exists(self) -> bool:
        """
        Creates the BigQuery table if it does not exist.
        Returns True if table was created, False if it already existed.
        Propagates other exceptions.
        """
        try:
            self.client.get_table(self.full_table_id)
            return False
        except NotFound:
            schema = self.table_schema()
            table = bigquery.Table(self.full_table_id, schema=schema)
            self.client.create_table(table)
            return True

    def check_row_exists(self) -> bool:
        """
        Checks if a row with the same primary_error_message, component, and resource_name
        already exists in the BigQuery table.
        Propagates exceptions on failure.
        """
        if not all([self.primary_error_message, self.component, self.resource_name]):
            return False

        query = f"""
            SELECT COUNT(1) as count
            FROM `{self.full_table_id}`
            WHERE primary_error_message = @primary_error_message
              AND component = @component
              AND resource_name = @resource_name
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(
                    "primary_error_message", "STRING", self.primary_error_message
                ),
                bigquery.ScalarQueryParameter("component", "STRING", self.component),
                bigquery.ScalarQueryParameter(
                    "resource_name", "STRING", self.resource_name
                ),
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        for row in results:
            return row["count"] > 0
        return False

    def get_unique_error_rows(self) -> List[Dict[str, Any]]:
        """
        Retrieves unique error rows from the BigQuery table.
        Returns a list of dictionaries representing the unique error rows.
        Propagates exceptions on failure.
        """
        query = f"""
            SELECT
                *
            FROM `{self.full_table_id}`
        """
        query_job = self.client.query(query)
        results = query_job.result()
        return [dict(row) for row in results]
