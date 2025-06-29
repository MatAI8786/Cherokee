"""Flask blueprint exposing Cherokee API endpoints."""

from flask import Blueprint, jsonify, request
import os
from ..database import SessionLocal
from ..models import Token, Trade
from ..trading import PaperTrader
import asyncio

bp = Blueprint('api', __name__, url_prefix='/api')

# single PaperTrader instance used for the /trade endpoint
trader = PaperTrader()


@bp.get('/health')
def health():
    """Simple health endpoint used by the frontend."""
    return jsonify({'status': 'ok'})


@bp.get('/logs')
def get_logs():
    """Return the last lines of a log file (server or scanner)."""
    name = request.args.get('file', 'scanner')
    path = os.path.join('logs', f'{name}.log')
    if not os.path.exists(path):
        return jsonify({'error': 'log not found'}), 404
    with open(path, 'r') as f:
        lines = f.readlines()[-50:]
    return jsonify({'file': name, 'lines': lines})

@bp.route('/tokens')
def list_tokens():
    """Return all known tokens or filter by query string."""
    q = request.args.get('q')
    session = SessionLocal()
    query = session.query(Token)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            (Token.address.like(pattern)) |
            (Token.name.like(pattern)) |
            (Token.symbol.like(pattern))
        )
    tokens = query.all()
    data = [t.to_dict() for t in tokens]
    session.close()
    return jsonify(data)

@bp.route('/tokens/<address>')
def token_detail(address):
    """Return details for a single token or 404 if missing."""
    session = SessionLocal()
    token = session.query(Token).filter_by(address=address).first()
    session.close()
    if token:
        return jsonify(token.to_dict())
    return jsonify({'error': 'not found'}), 404


@bp.post('/tokens/<address>/reanalyze')
def reanalyze_token(address):
    """Re-run analysis for a token and update the database."""
    from ..analyzer.token_analyzer import TokenAnalyzer
    session = SessionLocal()
    analyzer = TokenAnalyzer(
        session,
        etherscan_api_key=os.getenv('ETHERSCAN_API_KEY', ''),
        bscscan_api_key=os.getenv('BSC_SCAN_API_KEY', '')
    )
    result = asyncio.run(analyzer.analyze(address))
    existing = session.query(Token).filter_by(address=address).first()
    if existing:
        for k, v in result.items():
            setattr(existing, k, v)
    else:
        existing = Token.from_dict(result)
        session.add(existing)
    session.commit()
    session.close()
    return jsonify(result)

@bp.route('/high-risk')
def high_risk():
    """List tokens flagged as High or Critical risk."""
    session = SessionLocal()
    tokens = session.query(Token).filter(Token.risk_level.in_(['High','Critical'])).all()
    data = [t.to_dict() for t in tokens]
    session.close()
    return jsonify(data)


@bp.route('/trades')
def list_trades():
    """Return all recorded paper and live trades."""
    session = SessionLocal()
    trades = session.query(Trade).order_by(Trade.timestamp.desc()).all()
    data = [t.to_dict() for t in trades]
    session.close()
    return jsonify(data)


@bp.route('/trade', methods=['POST'])
def create_trade():
    """Simulate a buy or sell using the paper trader."""
    data = request.get_json() or {}
    address = data.get('token_address')
    action = data.get('action')
    quantity = float(data.get('quantity', 0))
    price = float(data.get('price', 0))
    reason = data.get('reasoning', '')
    if not address or action not in {'BUY', 'SELL'} or quantity <= 0 or price <= 0:
        return jsonify({'error': 'invalid request'}), 400

    coro = trader.buy(address, quantity, price, reasoning=reason) if action == 'BUY' else trader.sell(address, quantity, price, reasoning=reason)
    success = asyncio.run(coro)
    if not success:
        return jsonify({'error': 'trade failed'}), 400

    return jsonify({'status': 'ok', 'balance': trader.balance})


@bp.post('/scan')
def scan_token():
    """Analyze a token address using the TokenAnalyzer and store the result."""
    data = request.get_json() or {}
    address = data.get('address')
    chain = data.get('chain', 'ethereum')
    if not address:
        return jsonify({'error': 'missing address'}), 400

    from ..analyzer.token_analyzer import TokenAnalyzer

    session = SessionLocal()
    analyzer = TokenAnalyzer(
        session,
        etherscan_api_key=os.getenv('ETHERSCAN_API_KEY', ''),
        bscscan_api_key=os.getenv('BSC_SCAN_API_KEY', '')
    )
    result = asyncio.run(analyzer.analyze(address, chain))
    existing = session.query(Token).filter_by(address=address).first()
    if existing:
        for k, v in result.items():
            setattr(existing, k, v)
    else:
        existing = Token.from_dict(result)
        session.add(existing)
    session.commit()
    session.close()
    return jsonify(result)
