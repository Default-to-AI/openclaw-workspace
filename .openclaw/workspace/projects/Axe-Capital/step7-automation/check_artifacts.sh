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
    return 1
  fi
}

echo "Axe Capital artifact check"
echo "root: $ROOT_DIR"
echo

missing=0
check_file "normalized portfolio" "$ROOT_DIR/dashboard/data/portfolio_latest.normalized.csv" || missing=1
check_file "weekly review" "$ROOT_DIR/step6-dashboard/public/weekly-review-latest.json" || missing=1
check_file "dashboard portfolio" "$ROOT_DIR/step6-dashboard/public/portfolio.json" || missing=1
check_file "alpha latest" "$ROOT_DIR/step6-dashboard/public/alpha-latest.json" || missing=1
check_file "news latest" "$ROOT_DIR/step6-dashboard/public/news-latest.json" || missing=1
check_file "health" "$ROOT_DIR/step6-dashboard/public/health.json" || missing=1
check_file "trace index" "$ROOT_DIR/step6-dashboard/public/traces/index.json" || missing=1

exit "$missing"
