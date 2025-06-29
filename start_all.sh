#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
START_LOG="$LOG_DIR/startup_${TIMESTAMP}.log"
touch "$START_LOG"

VERBOSE=0
HEADLESS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose)
      VERBOSE=1
      ;;
    --headless)
      HEADLESS=1
      ;;
  esac
  shift
done

if [[ $VERBOSE -eq 1 ]]; then
  set -x
fi

INFO="\e[32m"
WARN="\e[33m"
ERR="\e[31m"
RESET="\e[0m"

log(){ echo -e "$1$2$RESET" | tee -a "$START_LOG"; }
info(){ log "$INFO" "[INFO] $*"; }
warn(){ log "$WARN" "[WARN] $*"; }
error(){ log "$ERR" "[ERROR] $*"; }

start_server(){
  info "Starting Cherokee API..."
  python -m cherokee.server 2>&1 | tee -a "$LOG_DIR/server.log" &
  SERVER_PID=$!
  sleep 2
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    error "API failed to start. Check $LOG_DIR/server.log"
    exit 1
  fi
  info "API started (PID $SERVER_PID)"
}

start_scanner(){
  info "Starting scanner..."
  python -m cherokee.run_scanner 2>&1 | tee -a "$LOG_DIR/scanner.log" &
  SCANNER_PID=$!
  sleep 2
  if ! kill -0 "$SCANNER_PID" 2>/dev/null; then
    error "Scanner failed to start. Check $LOG_DIR/scanner.log"
    exit 1
  fi
  info "Scanner started (PID $SCANNER_PID)"
}

health_check(){
  info "Performing health check on http://127.0.0.1:5000/api/health ..."
  if command -v curl >/dev/null; then
    if curl --max-time 5 -s http://127.0.0.1:5000/api/health >/dev/null; then
      info "API health check passed."
      return 0
    fi
  else
    python - <<'PY'
import urllib.request, sys
try:
    urllib.request.urlopen('http://127.0.0.1:5000/api/health', timeout=5)
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
    if [[ $? -eq 0 ]]; then
      info "API health check passed."
      return 0
    fi
  fi
  error "Health check failed! API not responding."
  tail -n 20 "$LOG_DIR/server.log" >&2 || true
  return 1
}

cleanup(){
  info "Stopping services..."
  [[ -n "${SERVER_PID:-}" ]] && kill "$SERVER_PID" 2>/dev/null || true
  [[ -n "${SCANNER_PID:-}" ]] && kill "$SCANNER_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

start_server
start_scanner
health_check || EXIT_CODE=1

if [[ "${EXIT_CODE:-0}" -ne 0 ]]; then
  error "Startup failed. See logs in $LOG_DIR."
else
  info "All services started successfully. Logs in $LOG_DIR."
fi

if [[ $HEADLESS -ne 1 ]]; then
  echo
  read -n 1 -s -r -p "Press any key to exit..." || true
fi
