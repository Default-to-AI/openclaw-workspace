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

