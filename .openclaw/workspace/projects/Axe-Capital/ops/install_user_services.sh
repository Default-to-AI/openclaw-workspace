#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_SRC="$ROOT_DIR/ops/systemd"
UNIT_DST="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

mkdir -p "$UNIT_DST"
install -m 0644 "$UNIT_SRC/axe-api.service" "$UNIT_DST/axe-api.service"
install -m 0644 "$UNIT_SRC/axe-dashboard.service" "$UNIT_DST/axe-dashboard.service"
install -m 0644 "$UNIT_SRC/axe-monthly-specialists.service" "$UNIT_DST/axe-monthly-specialists.service"
install -m 0644 "$UNIT_SRC/axe-monthly-specialists.timer" "$UNIT_DST/axe-monthly-specialists.timer"

systemctl --user daemon-reload
systemctl --user enable axe-api.service axe-dashboard.service axe-monthly-specialists.timer
systemctl --user restart axe-api.service axe-dashboard.service
systemctl --user start axe-monthly-specialists.timer

cat <<'MSG'
Axe Capital user services installed.

Dashboard:
  http://localhost:5173

Status:
  systemctl --user status axe-api.service
  systemctl --user status axe-dashboard.service
  systemctl --user list-timers axe-monthly-specialists.timer

Logs:
  journalctl --user -u axe-api.service -f
  journalctl --user -u axe-dashboard.service -f
MSG
