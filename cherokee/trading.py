import asyncio
from datetime import datetime
from typing import Dict

from .database import SessionLocal
from .models import Trade


class PaperTrader:
    """Simple paper trading engine that keeps track of a virtual balance."""

    def __init__(self, starting_balance: float = 10000.0):
        self.balance = starting_balance
        self.positions: Dict[str, float] = {}  # token_address -> quantity
        self.session = SessionLocal()

    async def buy(self, token_address: str, quantity: float, price: float, reasoning: str = ""):
        cost = quantity * price
        if self.balance < cost:
            return False
        self.balance -= cost
        self.positions[token_address] = self.positions.get(token_address, 0) + quantity
        trade = Trade(token_address=token_address, action="BUY", quantity=quantity, price=price,
                      reasoning=reasoning, is_live=0)
        self.session.add(trade)
        self.session.commit()
        return True

    async def sell(self, token_address: str, quantity: float, price: float, reasoning: str = ""):
        held = self.positions.get(token_address, 0)
        if held < quantity:
            return False
        self.positions[token_address] = held - quantity
        revenue = quantity * price
        self.balance += revenue
        trade = Trade(token_address=token_address, action="SELL", quantity=quantity, price=price,
                      reasoning=reasoning, is_live=0)
        self.session.add(trade)
        self.session.commit()
        return True

    def close(self):
        self.session.close()
