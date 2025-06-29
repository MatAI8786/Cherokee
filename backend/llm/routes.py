from flask import Blueprint, jsonify, request
from .providers import get_provider

bp = Blueprint("llm", __name__, url_prefix="/api/llm")

_HISTORY = []


@bp.post("/generate-logic")
def generate_logic():
    """Generate trading code or JSON logic using selected LLM."""
    data = request.get_json() or {}
    prompt = data.get("prompt", "")
    provider_id = data.get("provider", "openai-gpt4o")
    settings = data.get("settings", {})
    provider = get_provider(provider_id)
    if provider is None:
        return jsonify({"error": "unknown provider"}), 400
    try:
        code = provider.generate(prompt, settings)
    except Exception as exc:  # pragma: no cover - runtime errors
        return jsonify({"error": str(exc)}), 500
    entry = {"prompt": prompt, "provider": provider_id, "code": code}
    _HISTORY.append(entry)
    return jsonify(entry)


@bp.get("/history")
def history():
    """Return generated strategy history."""
    return jsonify(_HISTORY)
