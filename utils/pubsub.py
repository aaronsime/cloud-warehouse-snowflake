import json

from google.cloud.pubsub_v1 import PublisherClient

from config.base import settings


def publish_pubsub_message(topic: str, message: dict) -> str:
    """Publishes a message to the specified Pub/Sub topic."""
    publisher = PublisherClient()
    topic_path = publisher.topic_path(settings.PROJECT_ID, topic)

    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    message_id = future.result()

    return message_id
