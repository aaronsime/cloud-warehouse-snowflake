from google.cloud import storage  # type: ignore


def load_log_from_gcs(bucket_name: str, blob_name: str) -> str:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    log_bytes = blob.download_as_bytes()
    return log_bytes.decode("utf-8", errors="replace")
