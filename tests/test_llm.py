import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cherokee import database
from cherokee.web import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/llm.db"
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


def test_generate_logic(client):
    resp = client.post("/api/llm/generate-logic", json={"prompt": "Buy dip"})
    assert resp.status_code == 200
    assert "code" in resp.get_json()


def test_strategy_history(client):
    client.post("/api/strategies/deploy", json={"code": "print('hi')"})
    resp = client.get("/api/strategies/history")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1
