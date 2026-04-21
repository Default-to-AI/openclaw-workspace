from __future__ import annotations

import json
from pathlib import Path

from axe_orchestrator.projector import build_command_center_payload, write_command_center_artifacts


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_command_center_payload_normalizes_current_artifacts(tmp_path):
    _write_json(
        tmp_path / "health.json",
        {
            "generated_at": "2026-04-21T00:25:19Z",
            "artifacts": {
                "portfolio": {"last_refresh": "2026-04-21T00:25:19Z", "age_min": 0, "status": "fresh"},
                "decision": {"last_refresh": "2026-04-21T00:15:27Z", "age_min": 9, "status": "fresh"},
                "news": {"last_refresh": "2026-04-16T22:19:43Z", "age_min": 5885, "status": "stale"},
            },
        },
    )
    _write_json(
        tmp_path / "portfolio.json",
        {
            "generated_at": "2026-04-21T00:25:19Z",
            "data_source": "ibkr",
            "positions": [
                {
                    "symbol": "TSLA",
                    "shares": 2.0,
                    "weight_pct": 0.65,
                    "alert_status": "RED",
                    "distance_to_stop_pct": 2.08,
                    "stop_loss_level": 384.35,
                    "last_price": 392.5,
                },
                {
                    "symbol": "GOOG",
                    "shares": 40.0,
                    "weight_pct": 11.1,
                    "alert_status": "GREEN",
                    "distance_to_stop_pct": 22.51,
                    "stop_loss_level": 259.91,
                    "last_price": 335.4,
                },
            ],
            "summary": {"red_count": 1},
        },
    )
    _write_json(
        tmp_path / "position-state.json",
        {
            "updated_at": "2026-04-21",
            "positions": {
                "TSLA": {"thesis": "Speculative hold.", "target_price": 500.0, "stop_loss": 384.35},
                "GOOG": {"thesis": "AI monetization.", "target_price": 320.0, "stop_loss": 259.91},
            },
        },
    )
    _write_json(
        tmp_path / "decision-latest.json",
        {
            "run_id": "GOOG-1be743bb",
            "ticker": "GOOG",
            "candidate_type": "position_review",
            "generated_at": "2026-04-21T00:15:27Z",
            "status": "success",
            "ceo_action": "ADD",
            "ceo_conviction": 8,
            "ceo_thesis": "Thesis intact, add on dip",
        },
    )
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
    _write_json(
        tmp_path / "analyst-reports" / "index.json",
        {
            "generated_at": "2026-04-16T01:21:17Z",
            "symbols": {
                "GOOG": {
                    "fundamental": {
                        "json_path": "GOOG-fundamental.json",
                        "updated_at": "2026-04-21T00:11:00Z",
                    }
                }
            },
        },
    )

    payload = build_command_center_payload(tmp_path)

    assert payload["generated_at"] == "2026-04-21T00:25:19Z"
    assert payload["data_freshness"]["portfolio"]["status"] == "fresh"
    assert payload["current_focus"]["run_id"] == "GOOG-1be743bb"
    assert payload["decision_inbox"][0]["symbol"] == "GOOG"
    assert payload["decision_inbox"][0]["action"] == "ADD"
    assert payload["live_missions"][0]["run_id"] == "GOOG-1be743bb"
    assert payload["live_missions"][0]["status"] == "running"
    assert payload["watchers"][0]["key"] == "news"
    assert payload["watchers"][0]["status"] == "stale"
    assert payload["surveillance_alerts"][0]["symbol"] == "TSLA"
    assert payload["surveillance_alerts"][0]["severity"] == "RED"
    assert payload["firm_exceptions"][0]["key"] == "news"
    assert payload["firm_exceptions"][0]["status"] == "stale"


def test_build_command_center_payload_degrades_one_section_when_source_is_missing(tmp_path):
    _write_json(
        tmp_path / "health.json",
        {
            "generated_at": "2026-04-21T00:25:19Z",
            "artifacts": {
                "portfolio": {"last_refresh": "2026-04-21T00:25:19Z", "age_min": 0, "status": "fresh"},
                "decision": {"last_refresh": "2026-04-21T00:15:27Z", "age_min": 9, "status": "fresh"},
                "news": {"last_refresh": "2026-04-16T22:19:43Z", "age_min": 5885, "status": "stale"},
            },
        },
    )
    _write_json(tmp_path / "portfolio.json", {"generated_at": "2026-04-21T00:25:19Z", "positions": []})
    _write_json(tmp_path / "decision-latest.json", {"generated_at": "2026-04-21T00:15:27Z"})
    _write_json(tmp_path / "traces" / "index.json", {"generated_at": "2026-04-21T00:25:19Z", "runs": []})

    payload = build_command_center_payload(tmp_path)

    assert payload["partial"] is True
    assert payload["watchers"][0]["status"] == "missing"
    assert payload["watchers"][0]["partial"] is True
    assert payload["surveillance_alerts"] == []
    assert payload["decision_inbox"] == []


def test_write_command_center_artifacts_writes_static_payload_and_mission_index(tmp_path):
    _write_json(
        tmp_path / "health.json",
        {
            "generated_at": "2026-04-21T00:25:19Z",
            "artifacts": {
                "portfolio": {"last_refresh": "2026-04-21T00:25:19Z", "age_min": 0, "status": "fresh"},
            },
        },
    )
    _write_json(tmp_path / "portfolio.json", {"generated_at": "2026-04-21T00:25:19Z", "positions": []})
    _write_json(tmp_path / "decision-latest.json", {"generated_at": "2026-04-21T00:15:27Z"})
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
                }
            ],
        },
    )

    write_command_center_artifacts(tmp_path)

    command_center = json.loads((tmp_path / "command-center.json").read_text(encoding="utf-8"))
    mission_index = json.loads((tmp_path / "missions" / "index.json").read_text(encoding="utf-8"))

    assert command_center["generated_at"] == "2026-04-21T00:25:19Z"
    assert mission_index["missions"][0]["run_id"] == "GOOG-1be743bb"
