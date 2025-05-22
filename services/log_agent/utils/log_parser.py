import re
from typing import Dict, Optional


class LogParser:
    """
    Parses GCP log entries to extract useful information.
    """

    def __init__(self, log_entry: Dict):
        self.log_entry = log_entry

    def parse(self) -> Dict:
        """
        Extracts useful info from a GCP log entry.
        """
        parsed = {
            "timestamp": self.log_entry.get("timestamp"),
            "severity": self.log_entry.get("severity"),
            "error_message": None,
            "stack_trace": None,
            "component": None,
            "resource_name": None,
        }

        resource = self.log_entry.get("resource", {})
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

        if "textPayload" in self.log_entry:
            text = self.log_entry["textPayload"]
            parsed["error_message"] = self.extract_error_message(text)
            parsed["stack_trace"] = self.extract_stack_trace(text)
        elif "jsonPayload" in self.log_entry:
            message = self.log_entry["jsonPayload"].get("message", "")
            parsed["error_message"] = self.extract_error_message(message)
            parsed["stack_trace"] = self.extract_stack_trace(message)

        return parsed

    @staticmethod
    def extract_error_message(text: str) -> Optional[str]:
        """
        Extracts the last line of an error (e.g., ValueError: something went wrong)
        """
        match = re.search(r"(?P<error>[\w.]+Error:.*)", text.strip())
        return match.group("error") if match else None

    @staticmethod
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
