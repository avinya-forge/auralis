import logging
from typing import Any, Dict

import httpx
import jinja2

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Generic HTTP client for OpenAI/Anthropic APIs.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send payload to LLM and return the response.
        Wraps request in try/except for error resilience.
        """
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.base_url, json=payload, headers=self.headers, timeout=30.0
                )
                response.raise_for_status()
                res: Dict[str, Any] = response.json()
                return res
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            return {"error": "Request error"}
        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Unexpected error"}


class PromptFactory:
    """
    Dynamic template-based prompt generation.
    """

    def __init__(self) -> None:
        self.env = jinja2.Environment(autoescape=True)

    def generate_prompt(self, template_str: str, **kwargs: Any) -> str:
        """
        Generate a prompt string from a Jinja2 template and kwargs.
        Sanitizes inputs using autoescape=True in the Jinja environment.
        """
        template = self.env.from_string(template_str)
        return template.render(**kwargs)
