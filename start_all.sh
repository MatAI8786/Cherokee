#!/bin/bash
# Start Cherokee API and scanner with basic logging and auto-restart.
set -e

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

start_server() {
  while true; do
    echo "[server] starting" >> "$LOG_DIR/server.log"
    python -m cherokee.server >> "$LOG_DIR/server.log" 2>&1 || true
    echo "[server] crashed, restarting in 2s" >> "$LOG_DIR/server.log"
    sleep 2
  done
}

start_scanner() {
  while true; do
    echo "[scanner] starting" >> "$LOG_DIR/scanner.log"
    python -m cherokee.run_scanner >> "$LOG_DIR/scanner.log" 2>&1 || true
    echo "[scanner] crashed, restarting in 2s" >> "$LOG_DIR/scanner.log"
    sleep 2
  done
}


start_server &
SERVER_PID=$!
sleep 2
start_scanner &
SCANNER_PID=$!

trap 'kill $SERVER_PID $SCANNER_PID' INT TERM
wait $SERVER_PID $SCANNER_PID
