import json
from typing import Any, Dict, List, Optional, TypedDict

import anthropic

from config.base import settings


class AIResultTypedDict(TypedDict):
    summary: str
    role: str
    score: int


class AILogAttemptTypedDict(TypedDict):
    role: str
    summary_attempt: str
    score: int


def score_summary(text: str) -> int:
    """Scores the AI-generated summary based on key criteria."""
    score = 0
    if "**Summary**" in text:
        score += 1
    if "**Probable Cause**" in text:
        score += 1
    if "**Suggested Fix**" in text:
        score += 1
    if "```" in text:
        score += 1
    if len(text) < 2000:
        score += 1
    if len(text) > 10:
        score += 1
    return score


class ClaudeClient:
    """
    Client for interacting with the Claude API, using detailed parsed log information.
    """

    def __init__(
        self,
        dbt_run_summary: Dict[str, Any],
        orchestrator_context: Optional[Dict[str, Any]],
        failure_data_sample: Optional[List[Dict[str, Any]]],
    ) -> None:
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model_name = settings.ANTHROPIC_MODEL

        self.dbt_summary: Dict[str, Any] = dbt_run_summary
        self.orchestrator_context: Dict[str, Any] = (
            orchestrator_context if orchestrator_context else {}
        )
        self.failure_data_sample: Optional[List[Dict[str, Any]]] = failure_data_sample

    def build_prompt(self, role: str) -> str:
        """
        Constructs a detailed prompt for the LLM based on the role and parsed log data.
        """
        persona = {
            "engineer": "You are a senior cloud infrastructure and data engineering assistant.",
            "data_scientist": "You are a data scientist reviewing pipeline errors for impact.",
            "data_analyst": "You are a data analyst troubleshooting broken dashboards or missing data.",
        }.get(role, "You are a data practitioner reviewing dbt logs for errors.")

        orch_parts: List[str] = []
        if self.orchestrator_context.get("orchestrator_job_name"):
            orch_parts.append(
                f"- Orchestrator Job: {self.orchestrator_context['orchestrator_job_name']}"
            )
        if self.orchestrator_context.get("schedule"):
            orch_parts.append(f"- Schedule: {self.orchestrator_context['schedule']}")
        if self.orchestrator_context.get("current_dbt_job_invoked"):
            orch_parts.append(
                f"- Current dbt Step (within orchestrator): {self.orchestrator_context['current_dbt_job_invoked']}"
            )

        dbt_command_source: Optional[str] = self.dbt_summary.get(
            "invocation_command"
        ) or self.orchestrator_context.get("current_dbt_command_executed")

        orchestrator_str: str = (
            "\n                ".join(orch_parts)
            if orch_parts
            else "No specific orchestrator job details provided."
        )

        dbt_details_parts: List[str] = [
            f"Log Parsed Timestamp: {self.dbt_summary.get('parsed_timestamp', 'N/A')}",
            f"Component: {self.dbt_summary.get('component', 'transformation')}",
            f"Resource/dbt Job Name: {self.dbt_summary.get('resource_name', 'unknown_dbt_job')}",
            f"Overall Status: {self.dbt_summary.get('status', 'unknown')} ({self.dbt_summary.get('severity', 'UNKNOWN')})",
        ]
        if self.dbt_summary.get("dbt_version"):
            dbt_details_parts.append(f"dbt Version: {self.dbt_summary['dbt_version']}")

        target_profile: Optional[str] = self.dbt_summary.get("target_profile")
        target_name: Optional[str] = self.dbt_summary.get("target_name")
        if target_profile and target_name:
            dbt_details_parts.append(f"dbt Target: {target_profile}/{target_name}")
        elif target_name:
            dbt_details_parts.append(f"dbt Target: {target_name}")

        if dbt_command_source:
            dbt_details_parts.append(f"dbt Invocation Command: {dbt_command_source}")
        if self.dbt_summary.get("final_summary_stats"):
            dbt_details_parts.append(
                f"Final dbt Stats Line: {self.dbt_summary['final_summary_stats']}"
            )

        failing_nodes: List[str] = self.dbt_summary.get("failing_nodes", [])
        if failing_nodes:
            failing_nodes_str = ", ".join(failing_nodes)
            dbt_details_parts.append(f"Failing dbt Nodes: {failing_nodes_str}")

        dbt_details_str: str = "\n                ".join(dbt_details_parts)

        primary_error_msg: str = self.dbt_summary.get(
            "primary_error_message", "No primary error message extracted."
        )
        detailed_error_breakdown: str = self.dbt_summary.get(
            "full_error_details", "No detailed error breakdown available."
        )
        log_snippet_list: List[str] = self.dbt_summary.get(
            "error_log_snippet", ["No relevant log snippet available."]
        )
        log_snippet: str = "\n                ".join(log_snippet_list)

        failing_data_rows_str = (
            "No specific failing data rows provided or applicable for this error type."
        )
        if self.failure_data_sample:
            failing_data_rows_str = (
                "Sample of Failing Data Rows (from dbt store_failures table):\n"
            )

            for i, row_dict in enumerate(self.failure_data_sample[:10]):
                formatted_row = {
                    k: str(v)[:75] + ("..." if len(str(v)) > 75 else "")
                    for k, v in row_dict.items()
                }
                try:
                    failing_data_rows_str += (
                        f"Row {i + 1}: {json.dumps(formatted_row)}\n"
                    )
                except TypeError:
                    failing_data_rows_str += f"Row {i + 1}: {str(formatted_row)} (JSON serialization failed)\n"

            if len(self.failure_data_sample) > 10:
                failing_data_rows_str += "  (...and potentially more rows)\n"

        return f"""
            {persona}
            Please analyze the following dbt run information and provide a precise, actionable summary for triaging an error.

            **Overall Context for this Request:**
            - The information below comes from an automated data pipeline that uses dbt for transformations.
            - Your role is to assist an on-call engineer in quickly understanding and resolving the issue.
            - The response **must be Slack-friendly**: under 2000 characters, use clear markdown formatting, and avoid conversational fluff.

            **Orchestration Details:**
                {orchestrator_str}

            **dbt Run Execution Details:**
                {dbt_details_str}

            **Primary Error Identified:**
                {primary_error_msg}

            **Detailed Error Breakdown (from dbt log analysis):**
            ```text
            {detailed_error_breakdown}
            ```

            **Sample of Failing Data Rows (if applicable, from dbt's store_failures table):**
            ```text
            {failing_data_rows_str}
            ```

            **Relevant Log Snippet Around First Error:**
            ```text
            {log_snippet}
            ```

            **Required Response Format (Use this exact structure):**
            1.  **Summary**: Concisely state what failed and the most direct cause.
            2.  **Probable Cause**: Elaborate on where the issue likely originated (e.g., specific model logic, test configuration, data issue). Mention the specific dbt node(s) if identified.
            3.  **Suggested Fix**:
                * Provide concrete, actionable steps for investigation and resolution.
                * If applicable, include diagnostic SQL queries (use markdown for code blocks).
                * Be brief but confident in your recommendations.

            **Avoid:**
            - Generic advice or over-explaining concepts.
            - Speculating wildly if the provided logs lack sufficient evidence for a definitive cause. Stick to what the logs indicate.
        """

    def summarise_best_role(self) -> AIResultTypedDict:
        """
        Generates summaries for different roles and returns the best one based on a scoring system.
        """
        client = anthropic.Anthropic(api_key=self.api_key)
        roles: List[str] = ["engineer", "data_scientist", "data_analyst"]
        all_results_log: List[AILogAttemptTypedDict] = []

        best_result_data: AIResultTypedDict = {
            "summary": "Could not generate a satisfactory AI summary.",
            "role": "unknown",
            "score": -1,
        }

        for role in roles:
            prompt = self.build_prompt(role)
            response = client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            summary_text_for_role: str = response.content[0].text.strip()
            current_score_for_role: int = score_summary(summary_text_for_role)

            if current_score_for_role > best_result_data["score"]:
                best_result_data["summary"] = summary_text_for_role
                best_result_data["role"] = role
                best_result_data["score"] = current_score_for_role

            all_results_log.append(
                AILogAttemptTypedDict(
                    role=role,
                    summary_attempt=summary_text_for_role,
                    score=current_score_for_role,
                )
            )
        return best_result_data


# Backward-compatible alias
GeminiClient = ClaudeClient
