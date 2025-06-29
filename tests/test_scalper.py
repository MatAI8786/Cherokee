import json
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cherokee import database
from cherokee.web import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/scalper.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", Session)
    monkeypatch.setenv("CHEROKEE_AUTO_SAMPLE", "0")
    monkeypatch.setenv("SCALPER_STRATEGY_DIR", str(tmp_path / "strategies"))
    from cherokee.web import api as api_module
    from cherokee.logic_playground import api as logic_api
    monkeypatch.setattr(api_module, "SessionLocal", Session, raising=False)
    monkeypatch.setattr(logic_api, "SessionLocal", Session, raising=False)
    database.init_db()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_scalper_spec(client):
    resp = client.get("/api/scalper/spec")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == "ScalperModuleV1"


def test_deploy_and_monitor_strategy(client, tmp_path):
    strategy = {"id": "demo", "modules": ["a"]}
    resp = client.post("/api/scalper/deploy", json=strategy)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "deployed"

    resp = client.get("/api/scalper/monitor")
    assert resp.status_code == 200
    assert "demo" in resp.get_json()["active"]

    resp = client.post("/api/scalper/stop", json={"id": "demo"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "stopped"
