from typing import Dict

import google.generativeai as genai

from config.base import settings


class GeminiClient:
    """
    Client for interacting with the Gemini LLM.
    """

    def __init__(self, parsed_log: Dict) -> None:
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.error_msg = parsed_log.get("error_message", "Unknown error")
        self.stack_trace = parsed_log.get("stack_trace", "")
        self.component = parsed_log.get("component", "unknown component")
        self.resource = parsed_log.get("resource_name", "unknown resource")
        genai.configure(api_key=self.api_key)

    def build_prompt(self) -> str:
        """
        Constructs a prompt for the LLM based on the parsed log.
        """
        prompt = f"""
                You are a cloud infrastructure assistant. Interpret the following log error and suggest a fix.
                -Limit the response to 1000 characters or less. Avoid unnecessary explanation or verbose formatting.
                -Likely errors will related to ingestion, transformation done in python and dbt.

                Component: {self.component}
                Resource: {self.resource}
                Error Message: {self.error_msg}

                Stack Trace:
                {self.stack_trace}

                Respond in this format:
                1. Summary:
                2. Probable Cause:
                3. Suggested Fix:
                """

        return prompt

    def summarise_error(self) -> str:
        """
        Generates a summary, root cause, and suggested fix using Gemini.
        """

        model = genai.GenerativeModel(self.model_name)
        prompt = self.build_prompt()
        response = model.generate_content(prompt)
        return response.text.strip()
