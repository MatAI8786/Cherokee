from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .database import Base
import logging

class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, index=True)
    chain = Column(String)
    name = Column(String)
    symbol = Column(String)
    risk_score = Column(Float)
    risk_level = Column(String)
    llm_reasoning = Column(Text)
    detected_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Token instance ignoring unknown fields."""
        valid_fields = {c.name for c in cls.__table__.columns}
        filtered = {}
        invalid = []
        for key, value in data.items():
            if key in valid_fields:
                filtered[key] = value
            else:
                invalid.append(key)
        if invalid:
            logging.getLogger(__name__).warning(
                "Ignoring invalid Token fields: %s", ", ".join(invalid)
            )
        return cls(**filtered)

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'chain': self.chain,
            'name': self.name,
            'symbol': self.symbol,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'llm_reasoning': self.llm_reasoning,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }


class Trade(Base):
    """Database model representing both paper and live trades."""

    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    token_address = Column(String, index=True)
    action = Column(String)  # 'BUY' or 'SELL'
    quantity = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_live = Column(Integer, default=0)  # 0 = paper trade, 1 = real trade
    pnl = Column(Float, default=0.0)
    reasoning = Column(String)

    def to_dict(self):
        return {
            'id': self.id,
            'token_address': self.token_address,
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_live': bool(self.is_live),
            'pnl': self.pnl,
            'reasoning': self.reasoning,
        }
