from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def axe_root() -> Path:
    return project_root().parent


def today_local_iso() -> str:
    return datetime.now(ZoneInfo("Asia/Jerusalem")).date().isoformat()
