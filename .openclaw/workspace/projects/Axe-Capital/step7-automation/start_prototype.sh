#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STEP6="$ROOT_DIR/step6-dashboard"
STEP7="$ROOT_DIR/step7-automation"
LOG_DIR="$STEP7/logs"
mkdir -p "$LOG_DIR"

resolve_python() {
  if [[ -n "${AXE_PYTHON_BIN:-}" ]]; then
    printf '%s' "$AXE_PYTHON_BIN"
    return
  fi
  if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    printf '%s' "$ROOT_DIR/.venv/bin/python"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi
  echo "No Python interpreter found" >&2
  exit 1
}

resolve_uvicorn() {
  if command -v uvicorn >/dev/null 2>&1; then
    command -v uvicorn
    return
  fi
  echo "uvicorn not found. Activate the project environment first." >&2
  exit 1
}

resolve_npm() {
  if [[ -n "${AXE_NPM_BIN:-}" ]]; then
    printf '%s' "$AXE_NPM_BIN"
    return
  fi
  if command -v npm >/dev/null 2>&1; then
    command -v npm
    return
  fi
  echo "npm not found" >&2
  exit 1
}

PYTHON_BIN="$(resolve_python)"
UVICORN_BIN="$(resolve_uvicorn)"
NPM_BIN="$(resolve_npm)"

API_LOG="$LOG_DIR/api.log"
DASH_LOG="$LOG_DIR/dashboard.log"

(
  cd "$STEP7"
  nohup "$UVICORN_BIN" axe_orchestrator.api:app --reload --port 8000 > "$API_LOG" 2>&1 &
  echo $! > "$LOG_DIR/api.pid"
)

(
  cd "$STEP6"
  nohup "$NPM_BIN" run dev -- --host 0.0.0.0 --port 5173 > "$DASH_LOG" 2>&1 &
  echo $! > "$LOG_DIR/dashboard.pid"
)

sleep 2

echo "Prototype launch started"
echo "API log: $API_LOG"
echo "Dashboard log: $DASH_LOG"
echo "Then run: cd $STEP7 && $PYTHON_BIN -m axe_orchestrator.cli run all"
