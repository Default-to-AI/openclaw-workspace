from __future__ import annotations

import json
import asyncio
from pathlib import Path
from unittest.mock import patch

from axe_alpha import cli as alpha_cli
from axe_alpha import alpha_scan
from axe_alpha.alpha_scan import Candidate
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


def test_load_live_held_symbols_reads_portfolio_json(tmp_path, monkeypatch):
    public = tmp_path / "public"
    public.mkdir()
    (public / "portfolio.json").write_text(
        json.dumps(
            {
                "positions": [
                    {"symbol": "GOOG", "position": 1},
                    {"symbol": "QQQ", "shares": 2},
                    {"symbol": "MSFT", "position": 0},
                    {"symbol": "Cash", "position": 100},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(alpha_scan, "public_dir", lambda: public)

    assert alpha_scan.load_live_held_symbols() == {"GOOG", "QQQ"}


def test_filter_out_held_candidates_uses_live_portfolio():
    candidates = [
        Candidate("GOOG", "earnings_drift", "test", "held", {}, "2026-04-16T00:00:00Z", 7.0),
        Candidate("RTX", "earnings_drift", "test", "outside", {}, "2026-04-16T00:00:00Z", 6.8),
    ]

    filtered = alpha_scan.filter_out_held_candidates(candidates, {"GOOG"})

    assert [candidate.ticker for candidate in filtered] == ["RTX"]


def test_alpha_scan_falls_back_when_llm_summary_times_out(monkeypatch):
    candidate = Candidate(
        "RTX",
        "earnings_drift",
        "test",
        "forward EPS up with muted reaction",
        {"reaction_pct": 1.2},
        "2026-04-16T00:00:00Z",
        6.9,
    )

    monkeypatch.setattr(alpha_scan, "_load_investor_profile", lambda: "### IBKR Holdings — Current Positions\n")
    monkeypatch.setattr(alpha_scan, "load_live_held_symbols", lambda: set())

    async def fake_sync_stage(label, func, timeout_s, *args):
        return [candidate] if label == "8-K scan" else []

    async def fake_async_stage(label, awaitable, timeout_s):
        if hasattr(awaitable, "close"):
            awaitable.close()
        return []

    async def timeout_summary(client, api_key, candidate, profile_guardrail):
        raise TimeoutError()

    monkeypatch.setattr(alpha_scan, "_run_sync_stage", fake_sync_stage)
    monkeypatch.setattr(alpha_scan, "_run_async_stage", fake_async_stage)
    monkeypatch.setattr(alpha_scan, "_llm_summarize_candidate", timeout_summary)

    report = asyncio.run(alpha_scan.run_alpha_hunter_scan(api_key="sk-test"))

    assert report["opportunity_count_after_filter"] == 1
    assert report["top_opportunities"][0]["ticker"] == "RTX"
    assert report["top_opportunities"][0]["conviction_score"] == 7
    assert report["top_opportunities"][0]["why_retail_is_missing_this"] == "LLM summary unavailable; using detected trigger facts."


def test_options_flow_subprocess_boundary_parses_json(monkeypatch):
    calls = []

    class FakeCompleted:
        returncode = 0
        stdout = json.dumps(
            {
                "overview": {"pc_ratio": "0.7"},
                "flow": [
                    {"premium": 150000, "vol_gt_oi": False},
                    {"premium": 5000, "vol_gt_oi": True},
                ],
            }
        )
        stderr = ""

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return FakeCompleted()

    monkeypatch.setattr(alpha_scan.subprocess, "run", fake_run)

    data = alpha_scan._fetch_options_flow_data_subprocess("JPM", timeout_s=25)

    assert data["overview"]["pc_ratio"] == "0.7"
    assert data["flow"][0]["premium"] == 150000
    assert calls[0][1]["timeout"] == 30
