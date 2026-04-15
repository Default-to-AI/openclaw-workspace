#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

check_file() {
  local label="$1"
  local path="$2"
  if [[ -f "$path" ]]; then
    printf '[ok]   %s -> %s\n' "$label" "$path"
    ls -lh "$path" | awk '{print "       size=" $5 ", modified=" $6 " " $7 " " $8}'
  else
    printf '[miss] %s -> %s\n' "$label" "$path"
  fi
}

echo "Axe Capital artifact check"
echo "root: $ROOT_DIR"
echo

check_file "normalized portfolio" "$ROOT_DIR/dashboard/data/portfolio_latest.normalized.csv"
check_file "weekly review" "$ROOT_DIR/reports/weekly-review-latest.json"
check_file "dashboard portfolio" "$ROOT_DIR/step6-dashboard/public/portfolio.json"
check_file "alpha latest" "$ROOT_DIR/step6-dashboard/public/alpha-latest.json"
check_file "news latest" "$ROOT_DIR/step6-dashboard/public/news-latest.json"
check_file "health" "$ROOT_DIR/step6-dashboard/public/health.json"
check_file "trace index" "$ROOT_DIR/step6-dashboard/public/traces/index.json"
