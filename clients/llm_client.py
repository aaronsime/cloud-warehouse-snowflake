from typing import Dict

import google.generativeai as genai

# Only required locally; not needed in Cloud Run with proper IAM
genai.configure(api_key=None)


def summarise_error(parsed_log: Dict) -> str:
    """
    Generates a summary, root cause, and suggested fix using Gemini.
    """
    error_msg = parsed_log.get("error_message", "Unknown error")
    stack_trace = parsed_log.get("stack_trace", "")
    component = parsed_log.get("component", "unknown component")
    resource = parsed_log.get("resource_name", "unknown resource")

    prompt = f"""
            You are a cloud infrastructure assistant. Interpret the following log error and suggest a fix.

            Component: {component}
            Resource: {resource}
            Error Message: {error_msg}

            Stack Trace:
            {stack_trace}

            Respond in this format:
            1. Summary:
            2. Probable Cause:
            3. Suggested Fix:
            """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()
