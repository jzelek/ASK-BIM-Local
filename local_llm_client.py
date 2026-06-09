import json
import urllib.error
import urllib.request
from types import SimpleNamespace

from config import (
    LOCAL_LLM_API_KEY,
    LOCAL_LLM_API_KIND,
    LOCAL_LLM_BASE_URL,
    LOCAL_LLM_MAX_TOKENS,
    LOCAL_LLM_MODEL,
    LOCAL_LLM_TEMPERATURE,
    LOCAL_LLM_THINK,
    LOCAL_LLM_TIMEOUT_SECONDS,
)


class LocalLLMClient:
    """Small chat-completions client for a local LLM server."""

    def __init__(
        self,
        base_url=LOCAL_LLM_BASE_URL,
        model=LOCAL_LLM_MODEL,
        api_kind=LOCAL_LLM_API_KIND,
        api_key=LOCAL_LLM_API_KEY,
        timeout=LOCAL_LLM_TIMEOUT_SECONDS,
        temperature=LOCAL_LLM_TEMPERATURE,
        max_tokens=LOCAL_LLM_MAX_TOKENS,
        think=LOCAL_LLM_THINK,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_kind = api_kind
        self.api_key = api_key
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.think = think
        self.chat = _ChatResource(self)

    def _post_json(self, url, payload):
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Local LLM request failed with HTTP {error.code}: {details}"
            ) from error
        except urllib.error.URLError as error:
            raise RuntimeError(
                "Could not reach the local LLM server at "
                f"{url}. Start your local model server or set LOCAL_LLM_BASE_URL."
            ) from error

        return json.loads(response_body)

    def create_chat_completion(self, messages, model=None, temperature=None, **kwargs):
        if self.api_kind == "ollama":
            return self._create_ollama_chat(messages, model, temperature, **kwargs)
        return self._create_openai_compatible_chat(
            messages, model, temperature, **kwargs
        )

    def _create_ollama_chat(self, messages, model=None, temperature=None, **kwargs):
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": False,
            "think": kwargs.pop("think", self.think),
            "options": {
                "temperature": self.temperature if temperature is None else temperature,
                "num_predict": kwargs.pop("max_tokens", self.max_tokens),
            },
        }
        payload.update(kwargs)
        response = self._post_json(url, payload)
        return _to_namespace({"choices": [{"message": response["message"]}]})

    def _create_openai_compatible_chat(
        self, messages, model=None, temperature=None, **kwargs
    ):
        base_url = self.base_url
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"
        url = f"{base_url}/chat/completions"
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": (
                self.temperature if temperature is None else temperature
            ),
            "max_tokens": kwargs.pop("max_tokens", self.max_tokens),
            "stream": False,
        }
        payload.update(kwargs)
        return _to_namespace(self._post_json(url, payload))


class _ChatResource:
    def __init__(self, client):
        self.completions = _CompletionsResource(client)


class _CompletionsResource:
    def __init__(self, client):
        self.client = client

    def create(self, messages, model=None, temperature=None, **kwargs):
        return self.client.create_chat_completion(
            messages,
            model=model,
            temperature=temperature,
            **kwargs,
        )


def _to_namespace(value):
    if isinstance(value, dict):
        return SimpleNamespace(**{key: _to_namespace(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_to_namespace(item) for item in value]
    return value
