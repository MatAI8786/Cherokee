import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from cherokee import database
from cherokee.web import create_app
from cherokee.models import Token, Trade
from cherokee.trading import PaperTrader
from cherokee.analyzer import token_analyzer
from cherokee.analyzer.token_analyzer import TokenAnalyzer


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", Session)
    monkeypatch.setenv("CHEROKEE_AUTO_SAMPLE", "0")
    # propagate patched SessionLocal to modules that imported it
    from cherokee.web import api as api_module
    from cherokee import trading as trading_module
    monkeypatch.setattr(api_module, "SessionLocal", Session, raising=False)
    monkeypatch.setattr(trading_module, "SessionLocal", Session, raising=False)
    database.init_db()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_tokens_empty(client):
    resp = client.get("/api/tokens")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_token_detail_not_found(client):
    resp = client.get("/api/tokens/0xdeadbeef")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "not found"


def test_add_token_and_high_risk(client):
    session = database.SessionLocal()
    token = Token(address="0x1", chain="eth", name="Test", symbol="TST",
                  risk_score=0.9, risk_level="High")
    session.add(token)
    session.commit()

    resp = client.get("/api/tokens")
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["address"] == "0x1"

    resp = client.get("/api/tokens/0x1")
    assert resp.status_code == 200
    assert resp.get_json()["symbol"] == "TST"

    resp = client.get("/api/high-risk")
    high = resp.get_json()
    assert len(high) == 1
    assert high[0]["risk_level"] == "High"
    session.close()


@pytest.mark.asyncio
async def test_paper_trader_buy_sell(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/trade.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", Session)
    from cherokee import trading as trading_module
    monkeypatch.setattr(trading_module, "SessionLocal", Session, raising=False)
    database.init_db()

    trader = PaperTrader(starting_balance=100.0)
    result = await trader.buy("0x2", quantity=1, price=10.0)
    assert result is True
    assert trader.balance == 90.0

    result = await trader.sell("0x2", quantity=1, price=20.0)
    assert result is True
    assert trader.balance == 110.0

    session = database.SessionLocal()
    trades = session.query(Trade).all()
    assert len(trades) == 2
    trader.close()
    session.close()


@pytest.mark.asyncio
async def test_token_analyzer(monkeypatch, tmp_path):
    db_url = f"sqlite:///{tmp_path}/analyzer.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", Session)
    from cherokee.analyzer import token_analyzer as ta_module
    monkeypatch.setattr(ta_module, "SessionLocal", Session, raising=False)
    database.init_db()

    async def fake_fetch(self, address, chain):
        return {"result": [{"tokenName": "Fake", "symbol": "FAKE"}]}

    async def fake_eval(token_info):
        return {"score": 0.4, "reasoning": "test"}

    monkeypatch.setattr(TokenAnalyzer, "fetch_token_details", fake_fetch)
    monkeypatch.setattr(token_analyzer, "evaluate_risk", fake_eval)

    session = database.SessionLocal()
    analyzer = TokenAnalyzer(session)
    data = await analyzer.analyze("0x3")
    assert data["name"] == "Fake"
    assert data["risk_level"] == "Medium"
    assert "llm_reasoning" in data
    session.close()


def test_token_from_dict_filters_extra_fields():
    data = {
        "address": "0xabc",
        "chain": "eth",
        "name": "Extra",
        "symbol": "EXT",
        "risk_score": 0.1,
        "risk_level": "Low",
        "llm_reasoning": "looks safe",
        "reason": "ignore me",
    }
    token = Token.from_dict(data)
    assert token.address == "0xabc"
    assert token.llm_reasoning == "looks safe"
    assert not hasattr(token, "reason")


def test_token_search(client):
    session = database.SessionLocal()
    session.add(Token(address="0x1", chain="eth", name="Alpha", symbol="ALP", risk_score=0.1, risk_level="Low"))
    session.add(Token(address="0x2", chain="eth", name="Beta", symbol="BET", risk_score=0.9, risk_level="High"))
    session.commit()

    resp = client.get("/api/tokens?q=Alpha")
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["address"] == "0x1"
    session.close()


def test_reanalyze_endpoint(client, monkeypatch):
    session = database.SessionLocal()
    token = Token(address="0x3", chain="eth", name="Test", symbol="TST", risk_score=0.5, risk_level="Medium", llm_reasoning="old")
    session.add(token)
    session.commit()
    session.close()

    async def fake_analyze(self, address, chain="ethereum"):
        return {
            "address": address,
            "chain": chain,
            "name": "Test",
            "symbol": "TST",
            "risk_score": 0.9,
            "risk_level": "High",
            "llm_reasoning": "new",
        }

    monkeypatch.setattr(TokenAnalyzer, "analyze", fake_analyze)

    resp = client.post("/api/tokens/0x3/reanalyze")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["risk_level"] == "High"
    session = database.SessionLocal()
    updated = session.query(Token).filter_by(address="0x3").first()
    assert updated.risk_level == "High"
    assert updated.llm_reasoning == "new"
    session.close()
