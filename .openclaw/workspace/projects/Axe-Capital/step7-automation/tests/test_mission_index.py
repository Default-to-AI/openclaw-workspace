from __future__ import annotations

import json
from pathlib import Path

from axe_orchestrator.projector import build_mission_index


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_mission_index_keeps_latest_record_per_run_id(tmp_path):
    _write_json(
        tmp_path / "traces" / "index.json",
        {
            "generated_at": "2026-04-21T00:25:19Z",
            "runs": [
                {
                    "run_id": "GOOG-1be743bb",
                    "agent": "committee",
                    "started_at": "2026-04-21T00:10:00Z",
                    "ended_at": None,
                    "status": "running",
                    "summary": "committee run in progress",
                    "artifact_written": None,
                },
                {
                    "run_id": "GOOG-1be743bb",
                    "agent": "committee",
                    "started_at": "2026-04-21T00:10:00Z",
                    "ended_at": "2026-04-21T00:15:27Z",
                    "status": "success",
                    "summary": "committee decision complete",
                    "artifact_written": "decision-latest.json",
                },
                {
                    "run_id": "portfolio-21-04-2026T00-24-44Z",
                    "agent": "axe_portfolio",
                    "started_at": "2026-04-21T00:24:44Z",
                    "ended_at": "2026-04-21T00:25:19Z",
                    "status": "success",
                    "summary": "portfolio review",
                    "artifact_written": "portfolio.json",
                },
            ],
        },
    )

    mission_index = build_mission_index(tmp_path)

    assert mission_index["generated_at"] == "2026-04-21T00:25:19Z"
    assert len(mission_index["missions"]) == 1
    assert mission_index["missions"][0]["run_id"] == "GOOG-1be743bb"
    assert mission_index["missions"][0]["status"] == "completed"
    assert mission_index["missions"][0]["headline"] == "committee decision complete"


def test_build_mission_index_marks_active_and_terminal_states(tmp_path):
    _write_json(
        tmp_path / "traces" / "index.json",
        {
            "generated_at": "2026-04-21T00:25:19Z",
            "runs": [
                {
                    "run_id": "GOOG-running",
                    "agent": "committee",
                    "started_at": "2026-04-21T00:10:00Z",
                    "ended_at": None,
                    "status": "running",
                    "summary": "in progress",
                },
                {
                    "run_id": "AAPL-failed",
                    "agent": "committee",
                    "started_at": "2026-04-21T00:05:00Z",
                    "ended_at": "2026-04-21T00:09:00Z",
                    "status": "failed",
                    "summary": "analysis error",
                },
                {
                    "run_id": "TSLA-success",
                    "agent": "committee",
                    "started_at": "2026-04-21T00:01:00Z",
                    "ended_at": "2026-04-21T00:04:00Z",
                    "status": "success",
                    "summary": "decision complete",
                },
            ],
        },
    )

    mission_index = build_mission_index(tmp_path)

    missions_by_id = {m["run_id"]: m for m in mission_index["missions"]}

    running = missions_by_id["GOOG-running"]
    assert running["status"] == "running"
    assert running["ended_at"] is None
    assert running["source_updated_at"] == running["started_at"]
    assert running["staleness_state"] == "fresh"

    failed = missions_by_id["AAPL-failed"]
    assert failed["status"] == "failed"
    assert failed["ended_at"] == "2026-04-21T00:09:00Z"
    assert failed["source_updated_at"] == "2026-04-21T00:09:00Z"
    assert failed["staleness_state"] == "fresh"

    completed = missions_by_id["TSLA-success"]
    assert completed["status"] == "completed"
    assert completed["ended_at"] == "2026-04-21T00:04:00Z"
    assert completed["source_updated_at"] == "2026-04-21T00:04:00Z"
    assert completed["staleness_state"] == "fresh"

