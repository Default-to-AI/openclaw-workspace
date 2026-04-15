#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STEP6="$ROOT_DIR/step6-dashboard"
STEP7="$ROOT_DIR/step7-automation"
DECISION_LOG="$STEP6/public/decision-log.jsonl"

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

resolve_node() {
  if [[ -n "${AXE_NODE_BIN:-}" ]]; then
    printf '%s' "$AXE_NODE_BIN"
    return
  fi
  if command -v node >/dev/null 2>&1; then
    command -v node
    return
  fi
  echo "No Node.js runtime found" >&2
  exit 1
}

PYTHON_BIN="$(resolve_python)"
NODE_BIN="$(resolve_node)"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$STEP6/public"

echo "{\"ts\": \"$TIMESTAMP\", \"decision_type\": \"note\", \"tags\": [\"automation\", \"refresh\"], \"note\": \"daily refresh started\"}" >> "$DECISION_LOG"

(
  cd "$STEP7"
  "$PYTHON_BIN" -m axe_orchestrator.cli run all
)

(
  cd "$STEP6"
  "$NODE_BIN" scripts/sync_weekly_review_from_step5.mjs
)

(
  cd "$STEP7"
  "$PYTHON_BIN" -m axe_orchestrator.cli health
)

echo "{\"ts\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"decision_type\": \"note\", \"tags\": [\"automation\", \"refresh\"], \"note\": \"daily refresh complete\"}" >> "$DECISION_LOG"

echo "OK"
