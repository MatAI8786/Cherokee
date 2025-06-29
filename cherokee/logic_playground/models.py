from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from ..database import Base


class LogicGraph(Base):
    """Stored logic graph definition."""

    __tablename__ = "logic_graphs"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, default="")
    data = Column(Text)  # raw graph JSON
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Personality(Base):
    """Stored marketplace personality."""

    __tablename__ = "personalities"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    data = Column(Text)  # JSON configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
