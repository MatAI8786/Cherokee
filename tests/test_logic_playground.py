import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cherokee import database
from cherokee.web import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/logic.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", Session)
    monkeypatch.setenv("CHEROKEE_AUTO_SAMPLE", "0")
    from cherokee.web import api as api_module
    from cherokee.logic_playground import api as logic_api
    monkeypatch.setattr(api_module, "SessionLocal", Session, raising=False)
    monkeypatch.setattr(logic_api, "SessionLocal", Session, raising=False)
    database.init_db()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_save_and_load_graph(client):
    graph = {"nodes": [], "edges": []}
    resp = client.post("/api/logic/save", json={"name": "test", "graph": graph})
    assert resp.status_code == 200
    graph_id = resp.get_json()["id"]

    resp = client.get(f"/api/logic/load?id={graph_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "test"
    assert data["graph"] == graph


def test_simulate_graph(client):
    graph = {"nodes": [], "edges": []}
    resp = client.post("/api/logic/simulate", json={"graph": graph, "input": {}})
    assert resp.status_code == 200
    result = resp.get_json()
    assert result["status"] == "ok"
