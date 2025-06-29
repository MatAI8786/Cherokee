import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cherokee import database
from cherokee.web import create_app

@pytest.fixture
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/health.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", Session)
    monkeypatch.setenv("CHEROKEE_AUTO_SAMPLE", "0")
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_healthz(client):
    resp = client.get("/api/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_config_roundtrip(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "foo")
    resp = client.get("/api/config")
    data = resp.get_json()
    assert "OPENAI_API_KEY" in data
    resp = client.post("/api/config", json={"OPENAI_API_KEY": "bar"})
    assert resp.status_code == 200
    assert resp.get_json()["OPENAI_API_KEY"] == "bar"
