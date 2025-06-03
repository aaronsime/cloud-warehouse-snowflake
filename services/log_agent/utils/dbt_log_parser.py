import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TypedDict


class FailureDetailTypedDict(TypedDict, total=False):
    """
    Represents the structure of a single failure item, allowing for optional keys
    depending on the failure type.
    """

    type: str
    test_node_name: str
    node_name: str
    model_involved: Optional[str]
    message_summary: str
    raw_error_lines: List[str]
    filepath: Optional[str]
    detailed_reason: Optional[str]
    is_uniqueness_related: bool
    failure_storage_table: Optional[str]


class DBTLogSummaryTypedDict(TypedDict):
    """Defines the structure and types for the parsed dbt log summary."""

    parsed_timestamp: Optional[str]
    dbt_version: Optional[str]
    invocation_command: Optional[str]
    target_profile: Optional[str]
    target_name: Optional[str]
    test_failures: List[str]
    runtime_errors: List[str]
    detailed_failure_info: List[FailureDetailTypedDict]
    status: str
    exit_code: int
    final_summary_line: str
    should_save_log: bool
    failing_nodes: List[str]
    component: str
    resource_name: str
    severity: str
    primary_error_message: str
    full_error_details: str
    error_log_snippet: List[str]


class DBTLogParser:
    """
    Parses dbt log lines to extract test failures, runtime errors,
    invocation details, and overall status for LLM processing.
    """

    def __init__(self, log_lines: List[str]):
        self.log_lines: List[str] = log_lines
        self.failing_models_and_tests: Dict[str, Any] = {}
        self.current_test_failure_context: Optional[FailureDetailTypedDict] = None
        self._internal_failing_nodes_set: Set[str] = set()
        self.summary: DBTLogSummaryTypedDict = {
            "parsed_timestamp": None,
            "dbt_version": None,
            "invocation_command": None,
            "target_profile": None,
            "target_name": None,
            "test_failures": [],
            "runtime_errors": [],
            "detailed_failure_info": [],
            "status": "success",
            "exit_code": 0,
            "final_summary_line": "",
            "should_save_log": False,
            "failing_nodes": [],
            "component": "transformation",
            "resource_name": "transform-dbt",
            "severity": "INFO",
            "primary_error_message": "",
            "full_error_details": "",
            "error_log_snippet": [],
        }
        self._error_snippet_captured: bool = False

    @staticmethod
    def extract_model_from_test_name(full_test_node_name: str) -> Optional[str]:
        """
        Extracts a plausible model name from a dbt test node name.
        Example:
          'test.my_project.unique_with_rows_int__fact_orders_order_id.abc123hash'
          should return 'int__fact_orders'.
        """
        name_parts = full_test_node_name.split(".")
        relevant = name_parts[-1]
        if (
            len(name_parts) > 1
            and len(relevant) > 8
            and all(c in "0123456789abcdef" for c in relevant[-8:])
        ):
            relevant = name_parts[-2]

        prefixes = [
            "unique_with_rows_",
            "unique_",
            "not_null_",
            "accepted_values_",
            "relationships_",
            "primary_key_",
        ]
        for pfx in prefixes:
            if relevant.startswith(pfx):
                relevant = relevant[len(pfx) :]
                break

        if "__" not in relevant:
            parts = relevant.split("_")
            if not parts:
                return None

            common_suffixes = {
                "id",
                "uuid",
                "pk",
                "fk",
                "key",
                "date",
                "ts",
                "time",
                "timestamp",
                "name",
                "value",
                "code",
                "type",
                "status",
                "count",
                "desc",
                "amount",
                "qty",
                "ind",
            }
            while len(parts) > 1:
                last = parts[-1].lower()
                if last in common_suffixes or any(
                    last.endswith(suf) for suf in common_suffixes
                ):
                    parts.pop()
                else:
                    break

            return "_".join(parts) if parts else None

        left, right = relevant.split("__", 1)

        right_tokens = right.split("_")
        if len(right_tokens) >= 2:
            base_right = right_tokens[0] + "_" + right_tokens[1]
        else:
            base_right = right_tokens[0]

        return f"{left}__{base_right}"

    @staticmethod
    def clean_ansi_escapes(text: str) -> str:
        """
        Removes ANSI escape sequences from the text.
        """
        return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text).strip()

    def get_log_snippet(self, current_line_index: int, window: int = 5) -> List[str]:
        """
        Returns a snippet of log lines around the current line index
        """
        start = max(0, current_line_index - window // 2)
        end = min(len(self.log_lines), current_line_index + window // 2 + 1)
        return [self.clean_ansi_escapes(self.log_lines[i]) for i in range(start, end)]

    def finalize_current_test_failure_context(self) -> None:
        """
        Helper to finalize and store the current test failure context.
        """
        if self.current_test_failure_context:
            filepath = self.current_test_failure_context.get("filepath")
            if filepath:
                path_parts = filepath.replace("\\", "/").split("/")
                if "models" in path_parts and (
                    filepath.endswith(".yml") or filepath.endswith(".yaml")
                ):
                    model_filename = (
                        path_parts[-1].replace(".yml", "").replace(".yaml", "")
                    )
                    self.current_test_failure_context["model_involved"] = model_filename

            self.summary["detailed_failure_info"].append(
                self.current_test_failure_context
            )
            if "test_node_name" in self.current_test_failure_context:
                self._internal_failing_nodes_set.add(
                    self.current_test_failure_context["test_node_name"]
                )
            self.current_test_failure_context = None

    def process_log_line(self, line: str, line_idx: int) -> None:
        """
        Helper to process a single log line for the parse method.
        """
        if self.summary["parsed_timestamp"] is None:
            self.extract_timestamp(line)
        self.extract_metadata(line)

        if self.parse_test_failure_start(line, line_idx):
            return
        if self.parse_test_failure_details(line):
            return

        if self.current_test_failure_context and not line.startswith("[error]"):
            self.finalize_current_test_failure_context()

        if self.parse_dbt_core_error(line, line_idx):
            return

        if "Done. PASS=" in line and "ERROR=" in line and "TOTAL=" in line:
            self.summary["final_summary_line"] = line
            self.interpret_summary_stats(line)

    def parse(self) -> DBTLogSummaryTypedDict:
        """
        Parses all log lines and returns the structured summary.
        """
        for i, raw_line in enumerate(self.log_lines):
            line = self.clean_ansi_escapes(raw_line)
            if not line:
                continue
            self.process_log_line(line, i)

        self.finalize_current_test_failure_context()  # Finalize any open context after loop
        return self.finalize()

    def extract_timestamp(self, line: str) -> None:
        """
        Extracts the timestamp from a log line if present.
        """
        match = re.search(
            r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?|\d{2}:\d{2}:\d{2}\.\d{6})",
            line,
        )
        if match:
            self.summary["parsed_timestamp"] = match.group(1)

    def extract_metadata(self, line: str) -> None:
        """
        Extracts metadata such as dbt version, invocation command.
        """
        if self.summary["dbt_version"] is None:
            m = re.search(r"Running with dbt=([\d.]+)", line)
            if m:
                self.summary["dbt_version"] = m.group(1)

        if self.summary["invocation_command"] is None:
            m = re.search(r"'invocation_command': '([^']+)'", line)
            if m:
                self.summary["invocation_command"] = m.group(1)

        json_comment_match = re.search(r"\/\*\s*(\{.*?\})\s*\*\/", line)
        if json_comment_match:
            try:
                data: Dict[str, Any] = json.loads(json_comment_match.group(1))
                if self.summary["target_profile"] is None and "profile_name" in data:
                    self.summary["target_profile"] = str(data["profile_name"])
                if self.summary["target_name"] is None and "target_name" in data:
                    self.summary["target_name"] = str(data["target_name"])
            except json.JSONDecodeError:
                pass

    def parse_test_failure_start(self, line: str, line_idx: int) -> bool:
        """
        Parses the start of a test failure from a log line.
        """
        match = re.search(r"\[error\].*?\bFAIL\s+(\d+)\s+([a-zA-Z0-9_.]+)", line)
        if match:
            self.finalize_current_test_failure_context()
            self.set_status("warning", 0)
            failed_row_count = match.group(1)
            test_node_name_from_log = match.group(2)

            is_uniqueness_test = (
                test_node_name_from_log.startswith("unique_")
                or "unique_" in test_node_name_from_log.lower()
                or test_node_name_from_log.startswith("primary_key_")
            )

            self.current_test_failure_context = FailureDetailTypedDict(
                type="test_failure",
                test_node_name=test_node_name_from_log,
                model_involved=self.extract_model_from_test_name(
                    test_node_name_from_log
                ),
                message_summary=f"Test '{test_node_name_from_log}' failed on {failed_row_count} record(s).",
                raw_error_lines=[line],
                filepath=None,
                detailed_reason=None,
                is_uniqueness_related=is_uniqueness_test,
                failure_storage_table=None,
            )
            self.summary["test_failures"].append(line)
            if not self._error_snippet_captured:
                self.summary["error_log_snippet"] = self.get_log_snippet(line_idx)
                self._error_snippet_captured = True
            return True
        return False

    def parse_test_failure_details(self, line: str) -> bool:
        if self.current_test_failure_context and (
            line.startswith("[error]")
            or "See test failures:" in line
            or line.strip().startswith("select * from")
        ):

            self.current_test_failure_context.setdefault("raw_error_lines", []).append(
                line.strip()
            )

            path_match = re.search(r"Failure in test .* \(([^)]+)\)", line)
            if path_match:
                filepath = path_match.group(1).replace("\\", "/")
                self.current_test_failure_context["filepath"] = filepath
                if "/models/" in filepath and (
                    filepath.endswith(".yml") or filepath.endswith(".yaml")
                ):
                    model_yml_name = Path(filepath).stem
                    if model_yml_name:
                        self.current_test_failure_context["model_involved"] = (
                            model_yml_name
                        )

            reason_match = re.search(
                r"(Got \d+ results, configured to fail if .*)", line
            )
            if reason_match:
                self.current_test_failure_context["detailed_reason"] = (
                    reason_match.group(1)
                )

            storage_table_match = re.search(r"select \* from `([^`]+)`", line.strip())
            if storage_table_match:
                self.current_test_failure_context["failure_storage_table"] = (
                    storage_table_match.group(1)
                )
            return True
        return False

    def parse_dbt_core_error(self, line: str, line_idx: int) -> bool:
        """
        Parses dbt core errors from a log line.
        """
        error_keywords = [
            "Compilation Error",
            "Database Error",
            "Runtime Error while executing",
            "Encountered an error:",
        ]
        if any(keyword in line for keyword in error_keywords):
            self.finalize_current_test_failure_context()
            self.set_status("error", 1)
            self.summary["runtime_errors"].append(line)
            model_match = re.search(
                r"(?:model|seed|snapshot|source|test)\s+'([a-zA-Z0-9_.]+)'", line
            )
            node_name_from_log = (
                model_match.group(1) if model_match else "unknown_dbt_node"
            )
            core_error_detail: FailureDetailTypedDict = {
                "type": "dbt_core_error",
                "node_name": node_name_from_log,
                "message_summary": line,
                "raw_error_lines": [line],
            }
            self.summary["detailed_failure_info"].append(core_error_detail)
            self._internal_failing_nodes_set.add(node_name_from_log)
            if not self._error_snippet_captured:
                self.summary["error_log_snippet"] = self.get_log_snippet(line_idx)
                self._error_snippet_captured = True
            return True
        return False

    def interpret_summary_stats(self, line: str) -> None:
        """
        Interprets the summary statistics line to update the overall status.
        """
        match = re.search(r"ERROR=(\d+)", line)
        if match and int(match.group(1)) > 0:
            self.set_status("error", 1)

    def set_status(self, status: str, exit_code: int) -> None:
        """
        Sets the overall status of the dbt run based on the provided status and exit code.
        """
        if status == "error":
            self.summary["status"] = "error"
            self.summary["exit_code"] = exit_code
        elif status == "warning" and self.summary["status"] != "error":
            self.summary["status"] = "warning"
            self.summary["exit_code"] = exit_code
        if status in ["error", "warning"]:
            self.summary["should_save_log"] = True

    def determine_primary_error_message(self) -> str:
        """Helper to determine the primary error message for the summary."""
        if self.summary["detailed_failure_info"]:
            core_errors = [
                f_detail
                for f_detail in self.summary["detailed_failure_info"]
                if f_detail.get("type") == "dbt_core_error"
            ]
            if core_errors and core_errors[0].get("message_summary"):
                return core_errors[0]["message_summary"]
            if self.summary["detailed_failure_info"][0].get("message_summary"):
                return self.summary["detailed_failure_info"][0]["message_summary"]
        elif self.summary["runtime_errors"]:
            return self.summary["runtime_errors"][0]
        return ""

    def format_failure_details_for_llm(self) -> str:
        """Helper to format all failure details into a single string for the LLM."""
        details_for_llm: List[str] = []
        for failure in self.summary["detailed_failure_info"]:
            detail_parts: List[str] = [f"Type: {failure.get('type', 'unknown_type')}"]
            if failure.get("test_node_name"):
                detail_parts.append(f"Test Node: {failure['test_node_name']}")
            if failure.get("node_name"):
                detail_parts.append(f"Node: {failure['node_name']}")
            if failure.get("model_involved"):
                detail_parts.append(f"Model Involved: {failure['model_involved']}")
            detail_parts.append(f"Summary: {failure.get('message_summary', 'N/A')}")
            if failure.get("filepath"):
                detail_parts.append(f"Filepath: {failure['filepath']}")
            if failure.get("detailed_reason"):
                detail_parts.append(f"Reason: {failure['detailed_reason']}")

            raw_lines = failure.get("raw_error_lines", [])
            if raw_lines:
                detail_parts.append(
                    "Relevant Log Lines:\n"
                    + "\n".join(["  " + log_line for log_line in raw_lines])
                )
            details_for_llm.append("\n".join(detail_parts))
        return "\n---\n".join(details_for_llm)

    def finalize(self) -> DBTLogSummaryTypedDict:
        """Finalizes the summary dictionary with aggregated information."""
        if self.summary["status"] == "warning":
            self.summary["severity"] = "WARNING"
        elif self.summary["status"] == "error":
            self.summary["severity"] = "ERROR"

        self.summary["failing_nodes"] = sorted(list(self._internal_failing_nodes_set))
        self.summary["primary_error_message"] = self.determine_primary_error_message()

        if self.summary["detailed_failure_info"]:
            self.summary["full_error_details"] = self.format_failure_details_for_llm()
        elif self.summary["runtime_errors"]:
            self.summary["full_error_details"] = "\n".join(
                self.summary["runtime_errors"]
            )

        return self.summary
