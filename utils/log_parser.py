import re
from typing import Dict, Optional


def parse_log_entry(log_entry: Dict) -> Dict:
    """
    Extracts useful info from a GCP log entry.
    """
    parsed = {
        "timestamp": log_entry.get("timestamp"),
        "severity": log_entry.get("severity"),
        "error_message": None,
        "stack_trace": None,
        "component": None,
        "resource_name": None,
    }

    resource = log_entry.get("resource", {})
    resource_type = resource.get("type")
    labels = resource.get("labels", {})

    if resource_type == "cloud_function":
        parsed["component"] = (
            "transformation"
            if "transform" in labels.get("function_name", "")
            else "ingestion"
        )
        parsed["resource_name"] = labels.get("function_name")

    elif resource_type == "cloud_run_revision":
        parsed["component"] = (
            "transformation"
            if "transform" in labels.get("service_name", "")
            else "ingestion"
        )
        parsed["resource_name"] = labels.get("service_name")

    if "textPayload" in log_entry:
        text = log_entry["textPayload"]
        parsed["error_message"] = extract_error_message(text)
        parsed["stack_trace"] = extract_stack_trace(text)
    elif "jsonPayload" in log_entry:
        json_payload = log_entry["jsonPayload"]
        message = json_payload.get("message", "")
        parsed["error_message"] = extract_error_message(message)
        parsed["stack_trace"] = extract_stack_trace(message)

    return parsed


def extract_error_message(text: str) -> Optional[str]:
    """
    Extracts the last line of an error (e.g., ValueError: something went wrong)
    """
    match = re.search(r"(?P<error>[\w.]+Error:.*)", text.strip())
    if match:
        return match.group("error")
    return None


def extract_stack_trace(text: str) -> Optional[str]:
    """
    Extracts the full stack trace from a Python traceback.
    """
    if "Traceback (most recent call last):" in text:
        lines = text.strip().splitlines()
        traceback_lines = []
        in_traceback = False
        for line in lines:
            if "Traceback" in line:
                in_traceback = True
            if in_traceback:
                traceback_lines.append(line)
        return "\n".join(traceback_lines)
    return None
