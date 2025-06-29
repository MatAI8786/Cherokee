from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any

from flask import Blueprint, request, jsonify

bp = Blueprint("scalper", __name__, url_prefix="/api/scalper")

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "scalper.json"
STRATEGY_DIR = Path(os.getenv("SCALPER_STRATEGY_DIR", ROOT / "scalper_strategies"))
STRATEGY_DIR.mkdir(exist_ok=True)

# in-memory registry of deployed strategies for this process
_active: Dict[str, Dict[str, Any]] = {}


@bp.get("/spec")
def scalper_spec():
    """Return the canonical scalper JSON specification."""
    with open(SPEC_PATH, "r") as f:
        data = json.load(f)
    return jsonify(data)


@bp.get("/feed")
def scalper_feed():
    """Placeholder endpoint returning trending token data."""
    sample = [
        {"token": "SAMPLE", "price": 1.0, "volume24h": 1000, "hypeScore": 0.5, "newListing": False, "alerts": []}
    ]
    return jsonify(sample)


@bp.get("/sentiment")
def sentiment():
    """Return placeholder sentiment information for a token."""
    token = request.args.get("token", "SAMPLE")
    return jsonify({"token": token, "sentiment": 0.0})


@bp.post("/deploy")
def deploy_strategy():
    """Save and activate a scalper strategy."""
    data = request.get_json() or {}
    sid = data.get("id") or f"strategy_{len(_active)+1}"
    if not data.get("modules"):
        return jsonify({"error": "missing modules"}), 400
    path = STRATEGY_DIR / f"{sid}.json"
    with open(path, "w") as f:
        json.dump(data, f)
    _active[sid] = data
    return jsonify({"status": "deployed", "id": sid})


@bp.post("/stop")
def stop_strategy():
    sid = request.get_json(silent=True) or {}
    sid = sid.get("id")
    if sid and sid in _active:
        _active.pop(sid)
        return jsonify({"status": "stopped", "id": sid})
    return jsonify({"error": "not found"}), 404


@bp.get("/monitor")
def monitor():
    """Return list of active strategy ids."""
    return jsonify({"active": list(_active.keys())})
