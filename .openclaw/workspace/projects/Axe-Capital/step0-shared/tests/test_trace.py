from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from axe_core import trace as trace_mod
from axe_core.trace import Tracer


@pytest.fixture
def fake_public(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)
    (tmp_path / "traces").mkdir()
    return tmp_path


def test_tracer_writes_trace_file_and_index_entry(fake_public):
    t = Tracer(agent="axe_alpha", now=lambda: datetime(2026, 4, 15, 9, 0, tzinfo=timezone.utc))
    t.start()
    t.event(step="scan", thought="looking", io={"in": {"n": 1}, "out": {"n": 2}})
    t.event(step="done", thought="finished")
    t.finalize(status="success", summary="ran 2 steps", artifact_written="alpha-latest.json")

    trace_path = fake_public / "traces" / f"{t.run_id}.json"
    assert trace_path.exists()
    data = json.loads(trace_path.read_text())
    assert data["agent"] == "axe_alpha"
    assert data["status"] == "success"
    assert data["summary"] == "ran 2 steps"
    assert len(data["events"]) == 2
    assert data["events"][0]["seq"] == 1
    assert data["events"][1]["seq"] == 2

    index = json.loads((fake_public / "traces" / "index.json").read_text())
    assert len(index["runs"]) == 1
    assert index["runs"][0]["run_id"] == t.run_id
    assert index["runs"][0]["event_count"] == 2
    assert index["runs"][0]["artifact_written"] == "alpha-latest.json"


def test_run_id_uses_dd_mm_yyyy_format(fake_public):
    t = Tracer(agent="axe_alpha", now=lambda: datetime(2026, 4, 15, 9, 0, 0, tzinfo=timezone.utc))
    t.start()
    assert t.run_id.startswith("alpha-15-04-2026T09-00-00Z")


def test_finalize_is_atomic_via_tmp_rename(fake_public, monkeypatch):
    calls = []
    real_replace = Path.replace

    def spy(self, target):
        calls.append((self.name, Path(target).name))
        return real_replace(self, target)

    monkeypatch.setattr(Path, "replace", spy)
    t = Tracer(agent="axe_alpha")
    t.start()
    t.finalize(status="success", summary="ok")
    assert ("index.json.tmp", "index.json") in calls


def test_prune_keeps_newest_50_per_agent(fake_public):
    # Seed 60 fake alpha runs with prepopulated trace files
    now = datetime(2026, 4, 15, 9, 0, tzinfo=timezone.utc)
    for i in range(60):
        tr = Tracer(
            agent="axe_alpha",
            now=lambda i=i: datetime(2026, 4, 15, 9, i, 0, tzinfo=timezone.utc),
        )
        tr.start()
        tr.finalize(status="success", summary=f"run {i}")

    index = json.loads((fake_public / "traces" / "index.json").read_text())
    assert len(index["runs"]) == 50
    trace_files = list((fake_public / "traces").glob("alpha-*.json"))
    assert len(trace_files) == 50


def test_failed_runs_recorded_with_status(fake_public):
    t = Tracer(agent="axe_news")
    t.start()
    t.event(step="fetch", thought="fetching")
    t.finalize(status="failed", summary="RSS 500", artifact_written=None)
    data = json.loads((fake_public / "traces" / f"{t.run_id}.json").read_text())
    assert data["status"] == "failed"
    index = json.loads((fake_public / "traces" / "index.json").read_text())
    assert index["runs"][0]["status"] == "failed"
