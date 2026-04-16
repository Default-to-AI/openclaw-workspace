#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."

echo ""
echo "  AXE CAPITAL — dev launcher"
echo "  ─────────────────────────────────────────"
echo ""

# Check .env
if [ ! -f "$ROOT/.env" ]; then
  echo "  ERROR: .env not found at $ROOT/.env"
  echo "  Copy .env.example and fill in your keys."
  exit 1
fi

# Start API (step7)
echo "  Starting API (step7) on :8000 ..."
cd "$ROOT/step7-automation"
uvicorn axe_orchestrator.api:app --port 8000 --log-level warning &
API_PID=$!

# Give API a moment to start
sleep 2

# Health check
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
  echo "  API ready → http://localhost:8000"
else
  echo "  WARNING: API did not respond — dashboard will run in file-only mode"
fi

# Start dashboard (step6)
echo "  Starting dashboard (step6) on :5173 ..."
cd "$ROOT/step6-dashboard"
npm run dev &
DASH_PID=$!

echo ""
echo "  Dashboard → http://localhost:5173"
echo "  API      → http://localhost:8000"
echo ""
echo "  Press Ctrl+C to stop both."
echo ""

# On Ctrl+C, kill both
trap "kill $API_PID $DASH_PID 2>/dev/null; echo ''; echo '  Stopped.'; exit 0" INT TERM

wait
