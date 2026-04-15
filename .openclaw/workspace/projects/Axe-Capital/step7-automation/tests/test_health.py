from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from axe_orchestrator.health import compute_status, generate_health


def test_compute_status_buckets():
    now = datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc)
    fresh = (now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    stale = (now - timedelta(minutes=500)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert compute_status(fresh, 240, now=now)[1] == "fresh"
    assert compute_status(stale, 240, now=now)[1] == "stale"
    assert compute_status(None, 240, now=now) == (None, "missing")


def test_generate_health_reads_artifacts(tmp_path):
    public = tmp_path
    (public / "traces").mkdir()
    (public / "portfolio.json").write_text('{"generated_at":"2026-04-15T09:00:00Z"}')
    (public / "alpha-latest.json").write_text('{"generated_at":"2026-04-15T05:00:00Z"}')
    now = datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc)

    report = generate_health(public_dir=public, now=now)
    assert report["artifacts"]["portfolio"]["status"] == "fresh"
    assert report["artifacts"]["alpha"]["status"] == "fresh"
    assert report["artifacts"]["news"]["status"] == "missing"
    assert report["freshness_thresholds_min"] == {"portfolio": 240, "alpha": 1440, "news": 60}

    from axe_core.schemas import HealthReport
    HealthReport.model_validate(report)
