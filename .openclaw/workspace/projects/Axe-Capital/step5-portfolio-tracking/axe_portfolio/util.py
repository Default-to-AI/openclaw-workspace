from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def axe_root() -> Path:
    return project_root().parent


def today_local_iso() -> str:
    return datetime.now(ZoneInfo("Asia/Jerusalem")).date().isoformat()


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_float(value: Any) -> float | None:
    """Canonical float coercion. Strips commas, $, %, Unicode minus, leading +."""
    try:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = (
                value.strip()
                .replace(",", "")
                .replace("$", "")
                .replace("%", "")
                .replace("\u2212", "-")
            )
            if cleaned.startswith("+"):
                cleaned = cleaned[1:]
            if not cleaned:
                return None
            return float(cleaned)
        return float(value)
    except Exception:
        return None
