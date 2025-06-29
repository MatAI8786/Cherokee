from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = 'sqlite:///cherokee.db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def ensure_schema():
    """Add missing columns if the database was created with an older version."""
    with engine.begin() as conn:
        res = conn.execute(text("PRAGMA table_info(tokens)")).fetchall()
        columns = [r[1] for r in res]
        if "llm_reasoning" not in columns:
            conn.execute(text("ALTER TABLE tokens ADD COLUMN llm_reasoning TEXT"))


def init_db():
    Base.metadata.create_all(bind=engine)
    ensure_schema()


def populate_sample_data():
    """Insert sample token and trade records if tables are empty."""
    from .models import Token, Trade

    session = SessionLocal()
    if not session.query(Token).first():
        token = Token(
            address="0xsample",
            chain="eth",
            name="SampleToken",
            symbol="SAMP",
            risk_score=0.2,
            risk_level="Low",
        )
        session.add(token)
    if not session.query(Trade).first():
        trade = Trade(
            token_address="0xsample",
            action="BUY",
            quantity=1,
            price=1.0,
            reasoning="sample",
            is_live=0,
        )
        session.add(trade)
    session.commit()
    session.close()
