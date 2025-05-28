from typing import Any, Dict, List, Optional

import requests

from config.base import settings  # Assuming this is your settings module


class SlackMessenger:
    """
    Handles sending structured messages to Slack based on parsed log data and AI summaries.
    Errors from HTTP requests will propagate to the caller.
    """

    def __init__(
        self,
        parsed_log: Dict[str, Any],
        ai_summary: str,
        llm_role: Optional[str] = None,
        llm_score: Optional[int] = None,
    ) -> None:
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        self.timestamp = parsed_log.get(
            "parsed_timestamp", parsed_log.get("timestamp", "unknown")
        )
        self.component = parsed_log.get("component", "unknown_component")
        self.resource_name = parsed_log.get("resource_name", "unknown_resource")
        self.severity = parsed_log.get("severity", "ERROR")
        self.ai_summary_text = ai_summary
        self.llm_role_used = (
            llm_role if llm_role is not None else parsed_log.get("role", "unknown")
        )
        self.llm_score_value = (
            llm_score if llm_score is not None else parsed_log.get("score", 0)
        )
        # Ensure dbt_failing_nodes is treated as a list of strings if present
        self.dbt_failing_nodes: List[str] = parsed_log.get("failing_nodes", [])
        self.primary_error_message = parsed_log.get("primary_error_message", "")

    @staticmethod
    def _split_ai_summary_for_slack(
        text: str,
    ) -> Dict[str, str]:  # Renamed as it's an internal helper
        """
        Parses the AI-generated summary (expected to follow a 1., 2., 3. format)
        into structured parts for Slack formatting.
        """
        parts: Dict[str, str] = {"summary": "N/A", "cause": "N/A", "fix": "N/A"}
        current_part_key: Optional[str] = None

        if "AI summary generation failed" in text:
            parts["summary"] = text
            return parts

        for line in text.strip().splitlines():
            stripped_line = line.strip()
            if stripped_line.startswith("1.") or stripped_line.lower().startswith(
                "**summary**:"
            ):
                current_part_key = "summary"
                line_content = (
                    stripped_line.replace("1.", "", 1)
                    .replace("**summary**:", "", 1)
                    .strip()
                )
                parts[current_part_key] = line_content + "\n"
            elif stripped_line.startswith("2.") or stripped_line.lower().startswith(
                "**probable cause**:"
            ):
                current_part_key = "cause"
                line_content = (
                    stripped_line.replace("2.", "", 1)
                    .replace("**probable cause**:", "", 1)
                    .strip()
                )
                parts[current_part_key] = line_content + "\n"
            elif stripped_line.startswith("3.") or stripped_line.lower().startswith(
                "**suggested fix**:"
            ):
                current_part_key = "fix"
                line_content = (
                    stripped_line.replace("3.", "", 1)
                    .replace("**suggested fix**:", "", 1)
                    .strip()
                )
                parts[current_part_key] = line_content + "\n"
            elif current_part_key:
                parts[current_part_key] += line + "\n"
            else:
                if (
                    not parts["summary"] or parts["summary"] == "N/A"
                ):  # Prepend to summary if it's not started
                    parts["summary"] = (
                        (parts["summary"] if parts["summary"] != "N/A" else "")
                        + line
                        + "\n"
                    )

        for key in parts:
            parts[key] = parts[key].strip()
        return parts

    def format_slack_message_blocks(
        self,
    ) -> List[Dict[str, Any]]:  # Explicit return type
        """
        Formats the message blocks for the Slack notification.
        """
        parsed_ai_parts = self._split_ai_summary_for_slack(self.ai_summary_text)

        context_details = [
            f"*Component:* `{self.component}`",
            f"*Resource/Job:* `{self.resource_name}`",
            f"*Severity:* `{self.severity}`",
            f"*Log Timestamp:* `{self.timestamp}`",
        ]
        if self.primary_error_message:
            primary_err_snip = self.primary_error_message[:150]
            if len(self.primary_error_message) > 150:
                primary_err_snip += "..."
            context_details.append(f"*Primary Error:* `{primary_err_snip}`")

        if self.dbt_failing_nodes:  # This is now typed as List[str]
            failing_nodes_str = ", ".join(self.dbt_failing_nodes)
            context_details.append(f"*Failing dbt Nodes:* `{failing_nodes_str}`")

        context_details.extend(
            [
                f"*LLM Persona:* `{self.llm_role_used}`",
                f"*AI Summary Score:* `{self.llm_score_value}`",
            ]
        )

        blocks: List[Dict[str, Any]] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"⚠️ dbt Log Alert: {self.resource_name}",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "\n".join(context_details)},
            },
            {"type": "divider"},
        ]

        if parsed_ai_parts["summary"] and parsed_ai_parts["summary"] != "N/A":
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*1. AI Summary:*\n{parsed_ai_parts['summary']}",
                    },
                }
            )
        if parsed_ai_parts["cause"] and parsed_ai_parts["cause"] != "N/A":
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*2. AI Probable Cause:*\n{parsed_ai_parts['cause']}",
                    },
                }
            )

        fix_text = parsed_ai_parts["fix"]
        if fix_text and fix_text != "N/A":
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*3. AI Suggested Fix:*"},
                }
            )
            if "```" in fix_text:
                blocks.append(
                    {"type": "section", "text": {"type": "mrkdwn", "text": fix_text}}
                )
            else:
                blocks.append(
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"```{fix_text}```"},
                    }
                )
        return blocks

    def send_slack_notification(self) -> None:
        """
        Posts the formatted message to Slack.
        Raises requests.exceptions.HTTPError if the webhook request fails.
        """
        payload = {
            "text": f":warning: Error in dbt job: `{self.resource_name}` ({self.component})",
            "blocks": self.format_slack_message_blocks(),
        }
        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()
