"""API endpoints for the Logic Playground."""
from __future__ import annotations

import json
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .models import LogicGraph, Personality
from .runtime import LogicRuntime

bp = Blueprint("logic", __name__, url_prefix="/api")


@bp.post("/logic/save")
def save_graph():
    data = request.get_json() or {}
    name = data.get("name")
    graph_data = data.get("graph")
    if not name or not graph_data:
        return jsonify({"error": "missing name or graph"}), 400
    session: Session = SessionLocal()
    existing = session.query(LogicGraph).filter_by(name=name).first()
    if existing:
        existing.data = json.dumps(graph_data)
        existing.description = data.get("description", existing.description)
        existing.version += 1
    else:
        existing = LogicGraph(
            name=name,
            description=data.get("description", ""),
            data=json.dumps(graph_data),
        )
        session.add(existing)
    session.commit()
    resp = {"id": existing.id, "version": existing.version}
    session.close()
    return jsonify(resp)


@bp.get("/logic/load")
def load_graph():
    gid = request.args.get("id")
    name = request.args.get("name")
    session: Session = SessionLocal()
    query = session.query(LogicGraph)
    if gid:
        graph = query.filter_by(id=int(gid)).first()
    elif name:
        graph = query.filter_by(name=name).first()
    else:
        session.close()
        return jsonify({"error": "missing id or name"}), 400
    if not graph:
        session.close()
        return jsonify({"error": "not found"}), 404
    data = {
        "id": graph.id,
        "name": graph.name,
        "description": graph.description,
        "version": graph.version,
        "graph": json.loads(graph.data),
    }
    session.close()
    return jsonify(data)


@bp.post("/logic/simulate")
def simulate_graph():
    payload = request.get_json() or {}
    graph = payload.get("graph")
    if not graph:
        return jsonify({"error": "missing graph"}), 400
    runtime = LogicRuntime(graph)
    result = runtime.simulate(payload.get("input"))
    return jsonify(result)


@bp.post("/logic/deploy")
def deploy_graph():
    data = request.get_json() or {}
    graph = data.get("graph")
    if not graph:
        return jsonify({"error": "missing graph"}), 400
    # Placeholder: in real implementation this would hot-reload bot logic.
    return jsonify({"status": "deployed"})


@bp.get("/marketplace/personalities")
def list_personalities():
    session: Session = SessionLocal()
    items = session.query(Personality).all()
    data = [json.loads(p.data) | {"id": p.id, "name": p.name} for p in items]
    session.close()
    return jsonify(data)


@bp.post("/marketplace/personalities")
def save_personality():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "missing name"}), 400
    session: Session = SessionLocal()
    item = session.query(Personality).filter_by(name=name).first()
    if item:
        item.data = json.dumps(data)
    else:
        item = Personality(name=name, data=json.dumps(data))
        session.add(item)
    session.commit()
    resp = {"id": item.id}
    session.close()
    return jsonify(resp)


@bp.get("/marketplace/workflows")
def list_workflows():
    session: Session = SessionLocal()
    items = session.query(LogicGraph).all()
    data = [{"id": g.id, "name": g.name, "description": g.description} for g in items]
    session.close()
    return jsonify(data)


@bp.post("/marketplace/workflows")
def upload_workflow():
    # Reuse save_graph logic for simplicity
    return save_graph()
