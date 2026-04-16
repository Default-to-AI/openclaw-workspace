#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."

TARGET="${1:-}"

if [ -z "$TARGET" ]; then
  echo "Usage: ./scripts/refresh.sh <target>"
  echo ""
  echo "Targets:"
  echo "  portfolio          — refresh portfolio from IBKR"
  echo "  alpha              — run alpha hunter"
  echo "  news               — run news ingestion"
  echo "  specialists        — run fundamental/technical/macro for all holdings"
  echo "  specialists_decide — run specialists + decision memo"
  echo "  opportunities      — run for top alpha opportunities"
  echo "  all                — portfolio + alpha + news"
  exit 1
fi

echo "[axe refresh] target: $TARGET"
cd "$ROOT/step7-automation"
python -m axe_orchestrator.cli run "$TARGET"
echo "[axe refresh] done."
