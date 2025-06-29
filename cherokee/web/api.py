"""Flask blueprint exposing Cherokee API endpoints."""

from flask import Blueprint, jsonify, request
import os
import json
from pathlib import Path
import requests
from ..database import SessionLocal
from ..models import Token, Trade
from ..trading import PaperTrader
import asyncio

bp = Blueprint('api', __name__, url_prefix='/api')

# single PaperTrader instance used for the /trade endpoint
trader = PaperTrader()

# simple runtime state for new UI endpoints
SESSIONS = {}
BOT_STATE = {"running": False}
SETTINGS = {"darkModeEnabled": False, "timeZone": "UTC", "showTradesInTitle": False}
BACKTEST_RESULTS = {}
CONFIG_KEYS = [
    'GOOGLE_API_KEY',
    'OPENAI_API_KEY',
    'BINANCE_API_KEY',
    'ETHERSCAN_API_KEY',
    'BSC_SCAN_API_KEY',
]


@bp.get('/health')
def health():
    """Simple health endpoint used by the frontend."""
    return jsonify({'status': 'ok'})


@bp.get('/healthz')
def healthz():
    """Alias health check for consistency with tooling."""
    return jsonify({'status': 'ok'})


@bp.get('/service-status')
def service_status():
    """Return status for backend and scanner services."""
    scanner_ok = False
    try:
        r = requests.get('http://127.0.0.1:5001/healthz', timeout=2)
        if r.status_code == 200 and r.json().get('status') == 'ok':
            scanner_ok = True
    except Exception:
        scanner_ok = False
    return jsonify({'backend': 'ok', 'scanner': 'ok' if scanner_ok else 'down'})


@bp.get('/config')
def get_config():
    """Return current environment configuration values."""
    return jsonify({k: os.getenv(k, '') for k in CONFIG_KEYS})


@bp.post('/config')
def update_config():
    """Update environment variables in memory."""
    data = request.get_json() or {}
    for k, v in data.items():
        if k in CONFIG_KEYS:
            os.environ[k] = v
    return jsonify({k: os.getenv(k, '') for k in CONFIG_KEYS})


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


# ------------------ New UI Endpoints ------------------

@bp.get('/ui-spec')
def ui_spec():
    """Return the UI design specification JSON."""
    spec_path = Path(__file__).resolve().parents[2] / 'design.json'
    with open(spec_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)


@bp.post('/login')
def login():
    """Simple login endpoint storing session info."""
    data = request.get_json() or {}
    token = os.urandom(16).hex()
    SESSIONS[token] = {
        'botName': data.get('botName'),
        'apiUrl': data.get('apiUrl'),
        'username': data.get('username'),
    }
    return jsonify({'status': 'ok', 'token': token})


@bp.post('/start-bot')
def start_bot():
    BOT_STATE['running'] = True
    return jsonify({'running': True})


@bp.post('/stop-bot')
def stop_bot():
    BOT_STATE['running'] = False
    return jsonify({'running': False})


@bp.get('/open-trades')
def get_open_trades():
    session = SessionLocal()
    trades = session.query(Trade).order_by(Trade.timestamp.desc()).all()
    data = [t.to_dict() for t in trades]
    session.close()
    return jsonify(data)


@bp.get('/chart-data')
def chart_data():
    """Return placeholder candlestick data."""
    candles = [
        {'time': i, 'open': 100 + i, 'high': 102 + i, 'low': 99 + i, 'close': 101 + i}
        for i in range(10)
    ]
    return jsonify(candles)


@bp.get('/settings')
def get_settings():
    return jsonify(SETTINGS)


@bp.post('/settings')
def update_settings():
    SETTINGS.update(request.get_json() or {})
    return jsonify(SETTINGS)


@bp.post('/run-backtest')
def run_backtest():
    params = request.get_json() or {}
    BACKTEST_RESULTS['params'] = params
    BACKTEST_RESULTS['equity'] = [100, 110, 105]
    BACKTEST_RESULTS['summary'] = [{'Metric': 'Return', 'Value': '5%'}]
    return jsonify({'status': 'running'})


@bp.get('/backtest-results')
def backtest_results():
    return jsonify(BACKTEST_RESULTS)
