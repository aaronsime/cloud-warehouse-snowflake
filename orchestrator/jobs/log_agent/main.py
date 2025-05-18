import base64
import json

from flask import Flask, request

from clients.llm_client import GeminiClient
from config.base import settings
from config.logging import configure_logging
from utils.bq_storage import BigQueryService
from utils.log_parser import LogParser
from utils.slack_monitoring import SlackMessenger

app = Flask(__name__)


@app.route("/", methods=["POST"])
def pubsub_trigger() -> tuple[str, int]:

    log = configure_logging()
    log.info("Received Pub/Sub message")

    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return "Invalid Pub/Sub message", 400

    pubsub_message = envelope["message"]
    data = base64.b64decode(pubsub_message["data"]).decode("utf-8")

    log_entry = json.loads(data)
    parser = LogParser(log_entry=log_entry)
    log.info(f"Parsed log entry: {log_entry}")

    parsed = parser.parse()
    gemini_client = GeminiClient(parsed_log=parsed)
    log.info(f"Parsed log entry: {parsed}")

    summary = gemini_client.summarise_error()
    log.info(f"AI Summary: {summary}")

    bigquery_service = BigQueryService(parsed_log=parsed, ai_summary=summary)
    log.info("BigQuery service initialized")

    if bigquery_service.create_table_if_not_exists():
        log.info("Created BigQuery table")
    else:
        log.info("BigQuery table already exists")

    bigquery_service.log_to_bigquery()
    log.info(
        f"Logged error and AI summary inserted into {settings.TABLE_ERROR_SUMMARY} table"
    )

    slack_messenger = SlackMessenger(parsed_log=parsed, ai_summary=summary)
    slack_messenger.send_slack_notification()
    log.info("Slack notification sent successfully")

    return summary, 200


if __name__ == "__main__":

    result = pubsub_trigger()
    print(result)
