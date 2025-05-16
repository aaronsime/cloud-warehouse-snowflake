import base64
import json

from flask import Flask, request

from clients.llm_client import summarise_error
from utils.bq_logger import log_to_bigquery
from utils.log_parser import parse_log_entry
from utils.slack_monitoring import send_slack_notification

app = Flask(__name__)


@app.route("/", methods=["POST"])
def pubsub_trigger() -> tuple[str, int]:

    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return "Invalid Pub/Sub message", 400

    pubsub_message = envelope["message"]
    data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
    log_entry = json.loads(data)

    parsed = parse_log_entry(log_entry)
    summary = summarise_error(parsed)
    log_to_bigquery(parsed, summary)
    send_slack_notification(parsed, summary)

    return "Processed", 200


if __name__ == "__main__":
    pubsub_trigger()
