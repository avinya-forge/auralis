from unittest.mock import MagicMock, patch

import httpx

from src.services.ai.llm_orchestrator import LLMClient, PromptFactory


def test_prompt_factory_generation():
    factory = PromptFactory()
    template = "Hello, {{ name }}. You are {{ role }}."
    result = factory.generate_prompt(template, name="Alice", role="Admin")
    assert result == "Hello, Alice. You are Admin."


def test_prompt_factory_sanitization():
    factory = PromptFactory()
    template = "Message: {{ msg }}"
    result = factory.generate_prompt(template, msg="<script>alert(1)</script>")
    assert result == "Message: &lt;script&gt;alert(1)&lt;/script&gt;"


@patch("httpx.Client.post")
def test_llm_client_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"text": "response"}]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    client = LLMClient(base_url="https://api.openai.com/v1/completions", api_key="test_key")
    result = client.generate({"prompt": "Hello"})

    assert result == {"choices": [{"text": "response"}]}


@patch("httpx.Client.post")
def test_llm_client_http_error(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    mock_post.side_effect = httpx.HTTPStatusError(
        "HTTP error", request=MagicMock(), response=mock_response
    )

    client = LLMClient(base_url="https://api.openai.com/v1/completions", api_key="bad_key")
    result = client.generate({"prompt": "Hello"})

    assert result == {"error": "HTTP error 401"}


@patch("httpx.Client.post")
def test_llm_client_request_error(mock_post):
    mock_post.side_effect = httpx.RequestError("Connection timeout")

    client = LLMClient(base_url="https://api.openai.com/v1/completions", api_key="test_key")
    result = client.generate({"prompt": "Hello"})

    assert result == {"error": "Request error"}
