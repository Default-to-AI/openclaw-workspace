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

is_pid_running() {
  local pid="$1"
  [[ -n "$pid" ]] || return 1
  kill -0 "$pid" >/dev/null 2>&1
}

read_pidfile() {
  local path="$1"
  [[ -f "$path" ]] || return 1
  tr -d '[:space:]' < "$path"
}

pick_free_port() {
  local start="$1"
  local port="$start"
  while ss -ltn "sport = :$port" 2>/dev/null | tail -n +2 | grep -q .; do
    port=$((port+1))
  done
  printf '%s' "$port"
}

API_PID_FILE="$LOG_DIR/api.pid"
DASH_PID_FILE="$LOG_DIR/dashboard.pid"

# Clean up stale pid files so we don't lie to ourselves.
if pid="$(read_pidfile "$API_PID_FILE" 2>/dev/null || true)"; then
  if ! is_pid_running "$pid"; then
    rm -f "$API_PID_FILE"
  fi
fi
if pid="$(read_pidfile "$DASH_PID_FILE" 2>/dev/null || true)"; then
  if ! is_pid_running "$pid"; then
    rm -f "$DASH_PID_FILE"
  fi
fi

# If already running, don't start a second copy.
if pid="$(read_pidfile "$API_PID_FILE" 2>/dev/null || true)"; then
  if is_pid_running "$pid"; then
    echo "API already running (pid=$pid)"
  fi
fi
if pid="$(read_pidfile "$DASH_PID_FILE" 2>/dev/null || true)"; then
  if is_pid_running "$pid"; then
    echo "Dashboard already running (pid=$pid)"
  fi
fi

API_PORT="$(pick_free_port 8000)"
DASH_PORT="$(pick_free_port 5173)"

(
  cd "$STEP7"
  if [[ -f "$API_PID_FILE" ]]; then
    :
  else
    nohup "$UVICORN_BIN" axe_orchestrator.api:app --reload --port "$API_PORT" > "$API_LOG" 2>&1 &
    echo $! > "$API_PID_FILE"
  fi
)

(
  cd "$STEP6"
  if [[ -f "$DASH_PID_FILE" ]]; then
    :
  else
    nohup "$NPM_BIN" run dev -- --host 0.0.0.0 --port "$DASH_PORT" > "$DASH_LOG" 2>&1 &
    echo $! > "$DASH_PID_FILE"
  fi
)

sleep 2

echo "Prototype launch started"
echo "API log: $API_LOG"
echo "Dashboard log: $DASH_LOG"
echo "API: http://127.0.0.1:$API_PORT"
echo "Dashboard: http://localhost:$DASH_PORT"
echo "Then run: cd $STEP7 && $PYTHON_BIN -m axe_orchestrator.cli run all"
