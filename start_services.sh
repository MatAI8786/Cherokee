#!/usr/bin/env bash
set -euo pipefail
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

run_with_restart() {
  local cmd="$1"
  local log="$2"
  while true; do
    echo "Starting $cmd" | tee -a "$log"
    bash -c "$cmd" >> "$log" 2>&1 &
    pid=$!
    wait $pid && exit_code=$? || exit_code=$?
    echo "$(date) - $cmd exited with $exit_code" | tee -a "$log"
    sleep 1
  done &
  echo $!
}

if [ ! -d "frontend/node_modules" ] || [ ! -f "frontend/node_modules/.bin/react-scripts" ]; then
  echo "Installing frontend dependencies..."
  npm --prefix frontend install --no-audit --no-fund >> "$LOG_DIR/frontend.log" 2>&1
fi

UI_WATCH=$(run_with_restart "npm --prefix frontend start" "$LOG_DIR/frontend.log")
SERVER_WATCH=$(run_with_restart "python -m cherokee.server" "$LOG_DIR/server.log")

# wait for backend health
API_HEALTH=0
for i in {1..20}; do
  if curl -s http://127.0.0.1:5000/api/healthz >/dev/null 2>&1; then
    API_HEALTH=1
    break
  fi
  sleep 1
done
if [ "$API_HEALTH" -ne 1 ]; then
  echo "Backend failed to become healthy" | tee -a "$LOG_DIR/server.log"
  kill "$UI_WATCH" "$SERVER_WATCH" >/dev/null 2>&1 || true
  exit 1
fi

SCANNER_WATCH=$(run_with_restart "python -m cherokee.run_scanner" "$LOG_DIR/scanner.log")

trap "kill $UI_WATCH $SERVER_WATCH $SCANNER_WATCH" EXIT INT TERM
wait
