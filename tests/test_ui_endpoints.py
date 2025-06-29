import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cherokee import database
from cherokee.web import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/ui.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", Session)
    monkeypatch.setenv("CHEROKEE_AUTO_SAMPLE", "0")
    from cherokee.web import api as api_module
    from cherokee import trading as trading_module
    monkeypatch.setattr(api_module, "SessionLocal", Session, raising=False)
    monkeypatch.setattr(trading_module, "SessionLocal", Session, raising=False)
    database.init_db()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_ui_spec(client):
    resp = client.get("/api/ui-spec")
    assert resp.status_code == 200
    assert "sections" in resp.get_json()


def test_login_and_bot(client):
    resp = client.post("/api/login", json={"username": "u", "password": "p"})
    assert resp.status_code == 200
    token = resp.get_json().get("token")
    assert token

    resp = client.post("/api/start-bot")
    assert resp.status_code == 200
    assert resp.get_json()["running"] is True

    resp = client.post("/api/stop-bot")
    assert resp.status_code == 200
    assert resp.get_json()["running"] is False


def test_open_trades_empty(client):
    resp = client.get("/api/open-trades")
    assert resp.status_code == 200
    assert resp.get_json() == []
