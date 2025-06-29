import os
import logging
from pathlib import Path
from typing import Any, Dict, List

import requests

try:
    import openai
except Exception:  # pragma: no cover - openai optional
    openai = None

from backend.llm.providers import get_provider

# ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
if not logger.handlers:
    fh = logging.FileHandler("logs/llm_errors.log")
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
logger.setLevel(logging.INFO)

class LLMProviderError(Exception):
    """Represents a failure calling a specific provider."""

    def __init__(self, code: str, provider: str, details: str):
        super().__init__(details)
        self.code = code
        self.provider = provider
        self.details = details

class MultiProviderError(Exception):
    """Raised when all providers in the chain fail."""

    def __init__(self, errors: List[Dict[str, str]]):
        super().__init__("All providers failed")
        self.errors = errors

def _classify_exception(exc: Exception) -> str:
    """Map provider-specific exceptions to internal error codes."""
    if openai:
        if isinstance(exc, openai.RateLimitError):
            return "rate_limit_exceeded"
        if isinstance(exc, openai.PermissionDeniedError):
            return "quota_exceeded"
        if isinstance(exc, (openai.APIConnectionError, openai.APITimeoutError)):
            return "network_error"
        if isinstance(exc, openai.OpenAIError):
            return "api_error"
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return "network_error"
    return "unknown_error"

def _call_provider(provider_id: str, prompt: str, settings: Dict[str, Any]) -> str:
    provider = get_provider(provider_id)
    if provider is None:
        raise LLMProviderError("unknown_provider", provider_id, "Provider not configured")
    try:
        return provider.generate(prompt, settings)
    except Exception as exc:  # pragma: no cover - runtime errors
        code = _classify_exception(exc)
        logger.error("Provider %s failed: %s", provider_id, exc)
        raise LLMProviderError(code, provider_id, str(exc)) from exc

class LLMManager:
    """Handles LLM calls with provider fallback and error reporting."""

    def __init__(self, provider_order: List[str] | None = None):
        env_order = os.getenv("LLM_PROVIDER_ORDER")
        if provider_order is None:
            provider_order = env_order.split(",") if env_order else ["openai-gpt4o"]
        self.provider_order = [p for p in provider_order if p]

    def generate(
        self,
        prompt: str,
        settings: Dict[str, Any] | None = None,
        provider_order: List[str] | None = None,
    ) -> Dict[str, Any]:
        order = provider_order or self.provider_order
        settings = settings or {}
        errors: List[Dict[str, str]] = []
        for pid in order:
            try:
                text = _call_provider(pid, prompt, settings)
                return {"provider": pid, "text": text}
            except LLMProviderError as err:
                errors.append({"provider": err.provider, "error": err.code, "details": err.details})
        raise MultiProviderError(errors)
