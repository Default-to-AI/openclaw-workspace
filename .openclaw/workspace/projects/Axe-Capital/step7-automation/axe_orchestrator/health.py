"""Generate health.json from artifact metadata with timestamp and mtime fallback."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from axe_core.paths import public_dir

THRESHOLDS_MIN = {"portfolio": 240, "alpha": 1440, "news": 60}
ARTIFACT_FILES = {
    "portfolio": "portfolio.json",
    "alpha": "alpha-latest.json",
    "news": "news-latest.json",
    "traces": "traces/index.json",
}


def _read_generated_at(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        generated_at = data.get("generated_at")
        if generated_at:
            return generated_at
    except Exception:
        pass
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def compute_status(last_refresh: str | None, threshold_min: int, now: datetime) -> tuple[int | None, str]:
    if not last_refresh:
        return (None, "missing")
    try:
        ts = _parse_timestamp(last_refresh)
    except ValueError:
        return (None, "missing")
    age_min = int((now - ts).total_seconds() // 60)
    return (age_min, "fresh" if age_min <= threshold_min else "stale")


def generate_health(public_dir: Path, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    artifacts: dict = {}
    for key, rel in ARTIFACT_FILES.items():
        last = _read_generated_at(public_dir / rel)
        threshold = THRESHOLDS_MIN.get(key, 1440)
        age_min, status = compute_status(last, threshold, now=now)
        artifacts[key] = {"last_refresh": last, "age_min": age_min, "status": status}
    return {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifacts": artifacts,
        "freshness_thresholds_min": THRESHOLDS_MIN,
    }


def write_health() -> Path:
    pub = public_dir()
    report = generate_health(pub)
    out = pub / "health.json"
    tmp = out.with_name("health.json.tmp")
    tmp.write_text(json.dumps(report, indent=2))
    tmp.replace(out)
    return out
