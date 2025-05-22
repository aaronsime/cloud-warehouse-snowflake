from typing import Dict

import requests

from config.base import settings


class SlackMessenger:
    """
    Handles sending messages to Slack.
    """

    def __init__(self, parsed_log: Dict, ai_summary: str) -> None:
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        self.timestamp = parsed_log.get("timestamp", "unknown")
        self.component = parsed_log.get("component", "unknown")
        self.resource = parsed_log.get("resource_name", "unknown")
        self.severity = parsed_log.get("severity", "ERROR")
        self.summary = ai_summary

    def format_message(self) -> dict:
        """
        Formats the message to be sent to Slack.
        """

        message = {
            "text": f":warning: *Error Detected in `{self.component}`*",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Component:* `{self.component}`\n*Resource:* `{self.resource}`\n*Severity:* `{self.severity}`\n*Timestamp:* `{self.timestamp}`",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*AI Summary & Recommendation:*\n```{self.summary}```",
                    },
                },
            ],
        }

        return message

    def send_slack_notification(self) -> None:
        """
        Posts a formatted message to Slack with error context and AI suggestions.
        """

        response = requests.post(self.webhook_url, json=self.format_message())
        if response.status_code != 200:
            raise RuntimeError(f"Slack webhook failed: {response.text}")
