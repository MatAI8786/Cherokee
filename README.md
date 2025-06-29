# Cherokee2 Meme Token Scanner

Cherokee2 is a lightweight Flask API and on-chain scanner for experimental meme tokens. It exposes simple endpoints for querying discovered tokens and managing paper trades.

## Quick Start

```bash
cp .env.example .env  # add your API keys
pip install -r requirements.txt
./start_all.sh        # start API and scanner with logging
```

The API will be available at `http://127.0.0.1:5000`.

### Startup Script

`start_all.sh` launches the Flask API and the token scanner with colorized logs.
All output is written to `logs/` and streamed to the terminal. Use `--verbose`
for debug information or `--headless` when running on a server. After startup
the script performs a health check against `http://127.0.0.1:5000/api/health`.
If the check fails, the last lines of the server log are printed for quick
diagnostics.

Logs follow the pattern `logs/startup_YYYYMMDD_HHMMSS.log`, `logs/server.log`,
and `logs/scanner.log`.

## Running Tests

```bash
pytest -vv
```

## Environment Variables

The scanner uses API keys from `.env`:

- `OPENAI_API_KEY` – optional, improves risk analysis
- `ETHERSCAN_API_KEY` – for Ethereum token metadata
- `BSC_SCAN_API_KEY` – for Binance Smart Chain
- `CHEROKEE_AUTO_SAMPLE` – set `0` to disable sample records on startup

## Logic Playground

The Logic Playground is a visual editor for building custom AI workflows. It consists of a React front‑end under `frontend/logic_playground` and a Flask API module under `cherokee/logic_playground`.

### Development Setup

```bash
# install Python deps
pip install -r requirements.txt

# install frontend deps
cd frontend/logic_playground
npm install
npm run start
```

The app consumes the JSON specification in `logic_playground.json` and exposes the following key API endpoints:

- `POST /api/logic/save` – save a graph
- `GET /api/logic/load` – load a graph by `id` or `name`
- `POST /api/logic/simulate` – run a graph simulation
- `POST /api/logic/deploy` – deploy the graph

Marketplace endpoints allow saving and retrieving personalities and workflows.

## Scalper Module

The Scalper feature exposes a new set of API endpoints for building and deploying scalping strategies.

- `GET /api/scalper/spec` – return the `scalper.json` specification used by the UI
- `GET /api/scalper/feed` – live feed of trending tokens (stub data)
- `GET /api/scalper/sentiment?token=SYMBOL` – placeholder sentiment lookup
- `POST /api/scalper/deploy` – deploy a strategy JSON and store it under `scalper_strategies/`
- `POST /api/scalper/stop` – stop a running strategy by `id`
- `GET /api/scalper/monitor` – list currently active strategies

Strategies are saved as JSON files in the `scalper_strategies/` directory.
