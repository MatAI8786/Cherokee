import os
from typing import Any, Dict

class BaseProvider:
    """Base LLM provider."""

    def generate(self, prompt: str, settings: Dict[str, Any]) -> str:
        raise NotImplementedError


class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        try:
            import openai  # type: ignore
            self.client = openai.OpenAI(api_key=self.api_key)
        except Exception:  # pragma: no cover - openai may not be installed
            self.client = None

    def generate(self, prompt: str, settings: Dict[str, Any]) -> str:
        if not self.api_key or not self.client:
            # offline fallback
            return f"# Generated code placeholder for: {prompt}"
        resp = self.client.chat.completions.create(
            model=settings.get("model", "gpt-4o"),
            messages=[
                {"role": "system", "content": settings.get("systemPrompt", "")},
                {"role": "user", "content": prompt},
            ],
            temperature=settings.get("temperature", 0.2),
            max_tokens=settings.get("maxTokens", 2048),
        )
        return resp.choices[0].message.content


class SimpleHTTPProvider(BaseProvider):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def generate(self, prompt: str, settings: Dict[str, Any]) -> str:
        import requests

        try:
            r = requests.post(
                self.endpoint,
                json={"prompt": prompt, **settings},
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            return data.get("text") or data.get("code") or str(data)
        except Exception:
            return f"# Generated code placeholder for: {prompt}"


def get_provider(provider_id: str) -> BaseProvider | None:
    mapping = {
        "openai-gpt4o": OpenAIProvider(),
        "llama3": SimpleHTTPProvider(os.getenv("LLAMA3_ENDPOINT", "http://localhost:8000/v1")),
        "deepseek": SimpleHTTPProvider(os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1")),
        "starcoder": SimpleHTTPProvider(os.getenv("STARCODER_ENDPOINT", "http://localhost:9000/v1")),
        "custom": SimpleHTTPProvider(os.getenv("CUSTOM_LLM_ENDPOINT", "http://localhost:5001")),
    }
    return mapping.get(provider_id)
