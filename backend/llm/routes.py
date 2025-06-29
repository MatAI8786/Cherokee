from flask import Blueprint, jsonify, request

from cherokee.llm_manager import LLMManager, MultiProviderError, LLMProviderError

bp = Blueprint("llm", __name__, url_prefix="/api/llm")

_HISTORY = []

_manager = LLMManager()


@bp.post("/generate-logic")
def generate_logic():
    """Generate trading code or JSON logic using selected LLM."""
    data = request.get_json() or {}
    prompt = data.get("prompt", "")
    provider_id = data.get("provider")
    settings = data.get("settings", {})
    order = [provider_id] if provider_id else None
    try:
        result = _manager.generate(prompt, settings, order)
    except LLMProviderError as exc:  # single provider failed with no fallback
        return (
            jsonify({"error": exc.code, "provider": exc.provider, "details": exc.details}),
            502,
        )
    except MultiProviderError as exc:
        return jsonify({"error": "all_providers_failed", "details": exc.errors}), 503

    entry = {"prompt": prompt, "provider": result["provider"], "code": result["text"]}
    _HISTORY.append(entry)
    return jsonify(entry)


@bp.get("/history")
def history():
    """Return generated strategy history."""
    return jsonify(_HISTORY)
