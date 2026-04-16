#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."

API_PORT=8000
DASH_PORT=5173
API_URL="http://localhost:${API_PORT}"
DASH_URL="http://localhost:${DASH_PORT}"
API_DIR="$ROOT/step7-automation"
DASH_DIR="$ROOT/step6-dashboard"
API_CMD=(uvicorn axe_orchestrator.api:app --port "$API_PORT" --log-level info)
DASH_CMD=(npm run dev -- --port "$DASH_PORT" --strictPort)
API_PID=""
DASH_PID=""
MODE="start"
CLEANUP_ON_EXIT="1"

status_ok() {
  echo "OK: $*"
}

status_warning() {
  echo "WARNING: $*"
}

status_error() {
  echo "ERROR: $*" >&2
}

usage() {
  echo "Usage: bash scripts/dev.sh [--kill]"
  echo ""
  echo "Modes:"
  echo "  default   Kill stale Axe processes, then start API and dashboard"
  echo "  --kill    Kill stale Axe processes only, then exit"
}

process_summary() {
  ps -p "$1" -o pid=,ppid=,etime=,stat=,args= 2>/dev/null || true
}

wait_for_pids_to_exit() {
  local attempt
  local pid

  for attempt in {1..20}; do
    for pid in "$@"; do
      if kill -0 "$pid" 2>/dev/null; then
        sleep 0.25
        continue 2
      fi
    done
    return 0
  done

  return 1
}

kill_matching_processes() {
  local label="$1"
  local pattern="$2"
  local pid
  local pids

  mapfile -t pids < <(pgrep -f "$pattern" || true)
  if [ "${#pids[@]}" -eq 0 ]; then
    status_ok "No stale ${label} processes found"
    return 0
  fi

  status_warning "Found stale ${label} processes:"
  for pid in "${pids[@]}"; do
    process_summary "$pid"
  done

  for pid in "${pids[@]}"; do
    status_warning "Stopping ${label} PID ${pid}"
    kill "$pid" 2>/dev/null || true
  done

  if wait_for_pids_to_exit "${pids[@]}"; then
    status_ok "Cleared stale ${label} processes"
    return 0
  fi

  status_warning "${label} processes still running after SIGTERM; forcing shutdown"
  for pid in "${pids[@]}"; do
    kill -9 "$pid" 2>/dev/null || true
  done

  if wait_for_pids_to_exit "${pids[@]}"; then
    status_ok "Cleared stale ${label} processes after force kill"
    return 0
  fi

  status_error "Could not clear stale ${label} processes"
  return 1
}

stop_user_service_if_active() {
  local service="$1"

  if ! command -v systemctl >/dev/null 2>&1; then
    status_warning "systemctl is not available; skipping ${service} service check"
    return 0
  fi

  if ! systemctl --user cat "$service" > /dev/null 2>&1; then
    status_ok "User service ${service} not installed"
    return 0
  fi

  if systemctl --user is-active --quiet "$service"; then
    status_warning "Stopping user service ${service}"
    if systemctl --user stop "$service"; then
      status_ok "Stopped user service ${service}"
      return 0
    fi
    status_warning "Failed to stop user service ${service}; continuing with direct process cleanup"
    return 0
  fi

  status_ok "User service ${service} is not active"
}

run_fresh_cleanup() {
  echo ""
  echo "Fresh-start cleanup:"
  stop_user_service_if_active "axe-api.service"
  stop_user_service_if_active "axe-dashboard.service"
  kill_matching_processes "portfolio refresh" "axe_portfolio\\.cli|axe-portfolio-review"
  kill_matching_processes "Axe API" "axe_orchestrator\\.api:app"
  free_port "$API_PORT"
  free_port "$DASH_PORT"
}

port_pids() {
  lsof -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null || true
}

port_summary() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN 2>/dev/null | tail -n +2 || true
}

wait_for_port_to_clear() {
  local port="$1"
  local attempt

  for attempt in {1..20}; do
    if [ -z "$(port_pids "$port")" ]; then
      return 0
    fi
    sleep 0.25
  done

  return 1
}

free_port() {
  local port="$1"
  local pids
  local pid

  mapfile -t pids < <(port_pids "$port")
  if [ "${#pids[@]}" -eq 0 ]; then
    status_ok "Port ${port} is free"
    return 0
  fi

  status_warning "Port ${port} is in use:"
  port_summary "$port"

  for pid in "${pids[@]}"; do
    status_warning "Stopping PID ${pid} on port ${port}"
    kill "$pid" 2>/dev/null || true
  done

  if wait_for_port_to_clear "$port"; then
    status_ok "Port ${port} cleared"
    return 0
  fi

  status_warning "Port ${port} is still busy after SIGTERM; forcing shutdown"
  for pid in "${pids[@]}"; do
    kill -9 "$pid" 2>/dev/null || true
  done

  if wait_for_port_to_clear "$port"; then
    status_ok "Port ${port} cleared after force kill"
    return 0
  fi

  status_error "Could not clear port ${port}"
  return 1
}

wait_for_api() {
  local attempt

  for attempt in {1..20}; do
    if curl -sf "${API_URL}/health" > /dev/null 2>&1; then
      status_ok "API health check passed on ${API_URL}/health"
      return 0
    fi

    if [ -n "$API_PID" ] && ! kill -0 "$API_PID" 2>/dev/null; then
      status_error "API process exited before becoming healthy"
      return 1
    fi

    sleep 0.5
  done

  status_warning "API process is running but /health did not become ready yet"
  return 0
}

wait_for_dashboard() {
  local attempt

  for attempt in {1..20}; do
    if curl -sf "$DASH_URL" > /dev/null 2>&1; then
      status_ok "Dashboard responded on ${DASH_URL}"
      return 0
    fi

    if [ -n "$DASH_PID" ] && ! kill -0 "$DASH_PID" 2>/dev/null; then
      status_error "Dashboard process exited before serving requests"
      return 1
    fi

    sleep 0.5
  done

  status_warning "Dashboard process is running but ${DASH_URL} did not respond yet"
  return 0
}

stop_child() {
  local pid="$1"
  local name="$2"

  if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
    return 0
  fi

  status_warning "Stopping ${name} (PID ${pid})"
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
}

cleanup() {
  if [ "$CLEANUP_ON_EXIT" != "1" ]; then
    return 0
  fi
  kill_matching_processes "portfolio refresh" "axe_portfolio\\.cli|axe-portfolio-review"
  stop_child "$API_PID" "API"
  stop_child "$DASH_PID" "dashboard"
}

trap 'cleanup; echo ""; status_ok "Stopped."; exit 0' INT TERM
trap 'cleanup' EXIT

case "${1:-}" in
  "")
    ;;
  --kill|-k)
    MODE="kill"
    ;;
  --help|-h)
    CLEANUP_ON_EXIT="0"
    usage
    exit 0
    ;;
  *)
    CLEANUP_ON_EXIT="0"
    status_error "Unknown option: ${1}"
    usage
    exit 1
    ;;
esac

echo ""
echo "AXE CAPITAL — dev launcher"
echo "----------------------------------------"
echo "Command: bash scripts/dev.sh"
echo "Kill only: bash scripts/dev.sh --kill"
echo "Quick alias: axe-dev"
echo ""

if [ ! -f "$ROOT/.env" ]; then
  status_error ".env not found at $ROOT/.env"
  echo "Copy .env.example to .env before starting the stack."
  exit 1
fi

status_ok "Found .env at $ROOT/.env"
status_warning "Interactive Brokers is not checked by this launcher. Open TWS or IB Gateway if you need the API to talk to IBKR; the stack can still start now and connect later."

if [ "$MODE" = "kill" ]; then
  status_warning "Mode: cleanup only"
fi

run_fresh_cleanup

if [ "$MODE" = "kill" ]; then
  echo ""
  status_ok "Cleanup-only mode complete"
  CLEANUP_ON_EXIT="0"
  exit 0
fi

echo ""
echo "API command: (cd $API_DIR && ${API_CMD[*]})"
echo "API port: ${API_PORT}"
(cd "$API_DIR" && "${API_CMD[@]}") &
API_PID=$!
status_ok "Started API process with PID ${API_PID}"
wait_for_api

echo ""
echo "Dashboard command: (cd $DASH_DIR && ${DASH_CMD[*]})"
echo "Dashboard port: ${DASH_PORT}"
(cd "$DASH_DIR" && "${DASH_CMD[@]}") &
DASH_PID=$!
status_ok "Started dashboard process with PID ${DASH_PID}"
wait_for_dashboard

echo ""
status_ok "API URL: ${API_URL}"
status_ok "Dashboard URL: ${DASH_URL}"
echo "Press Ctrl+C to stop both."
echo ""

wait "$API_PID" "$DASH_PID"
