"""Simple script to exercise the new UI endpoints."""
import requests

BASE = "http://127.0.0.1:5000"


def main():
    s = requests.Session()
    r = s.post(f"{BASE}/api/login", json={"username": "demo"})
    print("login", r.status_code, r.json())

    s.post(f"{BASE}/api/start-bot")
    trades = s.get(f"{BASE}/api/open-trades").json()
    print("open trades", trades)
    s.post(f"{BASE}/api/stop-bot")
    r = s.post(f"{BASE}/api/run-backtest", json={"pair": "BTC/USD"})
    print("backtest", r.json())
    print("results", s.get(f"{BASE}/api/backtest-results").json())


if __name__ == "__main__":
    main()
