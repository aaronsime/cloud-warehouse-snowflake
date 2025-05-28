import ast
import re
from typing import Any, Dict, List


class OrchestratorLogParser:
    """
    Parses orchestration logs to extract key information about job execution and dbt command execution.
    Errors during parsing will propagate to the caller.
    """

    def __init__(self, log_lines: List[str]):
        self.log_lines = log_lines
        self.summary: Dict[str, Any] = {
            "orchestrator_job_name": None,
            "schedule": None,
            "current_dbt_job_invoked": None,
            "current_dbt_command_executed": None,
            "execution_sequence": [],
            "raw_log_snippet": [],
        }
        self._line_buffer: List[str] = []

    @staticmethod
    def clean_ansi_escapes(text: str) -> str:
        """Removes ANSI escape codes from a string and strips whitespace."""
        return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text).strip()

    def parse(self) -> Dict[str, Any]:
        """
        Parses the log lines.
        Errors from ast.literal_eval will propagate to the caller.
        """
        for raw_line in self.log_lines:
            line = self.clean_ansi_escapes(raw_line)
            if not line:
                continue

            self._line_buffer.append(line)
            if len(self._line_buffer) > 5:
                self._line_buffer.pop(0)

            env_match = re.search(
                r"Environment variables - JOB_NAME: (\w+), SCHEDULE: (\w+)", line
            )
            if env_match:
                self.summary["orchestrator_job_name"] = env_match.group(1)
                self.summary["schedule"] = env_match.group(2)

            seq_match = re.search(r"Ordered execution list resolved: (\[.*?\])", line)
            if seq_match:
                list_str = seq_match.group(1)
                self.summary["execution_sequence"] = ast.literal_eval(list_str)

            start_job_match = re.search(r"Starting dbt run for job: '([^']+)'", line)
            if start_job_match:
                self.summary["current_dbt_job_invoked"] = start_job_match.group(1)

            cmd_match = re.search(r"Running dbt command: (dbt .*)", line)
            if cmd_match:
                self.summary["current_dbt_command_executed"] = cmd_match.group(1)

        return self.summary
