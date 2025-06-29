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
