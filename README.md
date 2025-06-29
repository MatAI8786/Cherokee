# Cherokee2 Meme Token Scanner

Cherokee2 is a lightweight Flask API and on-chain scanner for experimental meme tokens. It exposes simple endpoints for querying discovered tokens and managing paper trades.

## Quick Start

```bash
cp .env.example .env  # add your API keys
pip install -r requirements.txt
./start_all.sh        # runs API and scanner with auto restart
```

The API will be available at `http://127.0.0.1:5000`.

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
