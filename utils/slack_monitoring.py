from typing import Dict

import requests

from config.base import settings


def send_slack_notification(parsed_log: Dict, ai_summary: str) -> None:
    """
    Posts a formatted message to Slack with error context and AI suggestions.
    """

    timestamp = parsed_log.get("timestamp", "unknown")
    component = parsed_log.get("component", "unknown")
    resource = parsed_log.get("resource_name", "unknown")
    severity = parsed_log.get("severity", "ERROR")

    message = {
        "text": f":warning: *Error Detected in `{component}`*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Component:* `{component}`\n*Resource:* `{resource}`\n*Severity:* `{severity}`\n*Timestamp:* `{timestamp}`",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*AI Summary & Recommendation:*\n```{ai_summary}```",
                },
            },
        ],
    }

    response = requests.post(settings.SLACK_WEBHOOK_URL, json=message)
    if response.status_code != 200:
        raise RuntimeError(f"Slack webhook failed: {response.text}")
