from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from axe_alpha import cli as alpha_cli
from axe_core import trace as trace_mod


def _fake_report() -> dict:
    return {
        "report_date": "2026-04-15",
        "generated_at": "2026-04-15T09:00:00Z",
        "top_opportunities": [
            {
                "ticker": "RTX",
                "opportunity_type": "earnings_drift",
                "thesis": "x",
                "conviction_score": 7,
                "trigger_source": "yfinance_earnings",
                "trigger_data_point": "d",
                "why_retail_is_missing_this": "w",
                "risk_flags": "r",
                "raw_facts": {},
                "base_score": 6.9,
            }
        ],
    }


def test_cli_emits_trace_and_writes_alpha_latest(tmp_path, monkeypatch):
    # Redirect public dir to tmp.
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)
    monkeypatch.setattr(alpha_cli, "public_dir", lambda: tmp_path)

    # Stub archival path to a tmp location.
    archive = tmp_path / "archive" / "2026-04-15.json"
    monkeypatch.setattr(alpha_cli, "report_path_for_date", lambda d: archive)

    # Stub env + network.
    monkeypatch.setattr(alpha_cli, "load_project_env", lambda: None)
    monkeypatch.setattr(alpha_cli, "openai_api_key", lambda: "sk-test")

    async def fake_run(api_key):
        return _fake_report()

    monkeypatch.setattr(alpha_cli, "run_alpha_hunter_scan", fake_run)

    alpha_cli.main()

    # alpha-latest.json written
    latest = json.loads((tmp_path / "alpha-latest.json").read_text())
    assert latest["report_date"] == "2026-04-15"
    # Archive also written
    assert archive.exists()
    # Trace file and index exist
    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert len(index["runs"]) == 1
    assert index["runs"][0]["agent"] == "axe_alpha"
    assert index["runs"][0]["artifact_written"] == "alpha-latest.json"
    assert index["runs"][0]["status"] == "success"


def test_cli_records_failure_in_trace(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)
    monkeypatch.setattr(alpha_cli, "public_dir", lambda: tmp_path)
    monkeypatch.setattr(alpha_cli, "load_project_env", lambda: None)
    monkeypatch.setattr(alpha_cli, "openai_api_key", lambda: "sk-test")

    async def boom(api_key):
        raise RuntimeError("upstream down")

    monkeypatch.setattr(alpha_cli, "run_alpha_hunter_scan", boom)

    try:
        alpha_cli.main()
    except RuntimeError:
        pass

    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert index["runs"][0]["status"] == "failed"
