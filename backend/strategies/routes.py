from flask import Blueprint, jsonify, request

bp = Blueprint("strategies", __name__, url_prefix="/api/strategies")

_HISTORY = []


@bp.post("/deploy")
def deploy_strategy():
    """Deploy provided trading code or logic to the bot."""
    data = request.get_json() or {}
    code = data.get("code") or data.get("logic")
    if not code:
        return jsonify({"error": "missing code"}), 400
    _HISTORY.append({"action": "deploy", "code": code})
    return jsonify({"status": "deployed"})


@bp.post("/simulate")
def simulate_strategy():
    """Simulate code in paper trading mode."""
    data = request.get_json() or {}
    code = data.get("code") or data.get("logic")
    if not code:
        return jsonify({"error": "missing code"}), 400
    result = {"status": "simulated", "logs": []}
    _HISTORY.append({"action": "simulate", "code": code, "result": result})
    return jsonify(result)


@bp.post("/import")
def import_strategy():
    data = request.get_json() or {}
    _HISTORY.append({"action": "import", "strategy": data})
    return jsonify({"status": "imported"})


@bp.get("/history")
def history():
    return jsonify(_HISTORY)
