#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

STEP5="$ROOT_DIR/step5-portfolio-tracking"
STEP6="$ROOT_DIR/step6-dashboard"

DECISION_LOG="$STEP6/public/decision-log.jsonl"
HEALTH_JSON="$STEP6/public/health.json"

ts_ms() {
  "$ROOT_DIR/.venv/bin/python" - <<'PY'
import time
print(int(time.time()*1000))
PY
}

TS="$(ts_ms)"

mkdir -p "$STEP6/public"

echo "{\"ts\": $TS, \"type\": \"run\", \"summary\": \"daily refresh started\"}" >> "$DECISION_LOG"

(
  cd "$STEP5"
  "$ROOT_DIR/.venv/bin/python" -m axe_portfolio.cli >/dev/null
)

(
  cd "$STEP6"
  npm run sync:weekly >/dev/null
)

cat > "$HEALTH_JSON" <<JSON
{
  "ts": $TS,
  "status": "OK",
  "notes": "daily refresh complete"
}
JSON

echo "{\"ts\": $TS, \"type\": \"run\", \"summary\": \"daily refresh complete\"}" >> "$DECISION_LOG"

echo "OK"
