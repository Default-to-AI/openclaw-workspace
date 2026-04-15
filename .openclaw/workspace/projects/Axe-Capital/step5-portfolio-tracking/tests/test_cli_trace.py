from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from axe_portfolio import cli as portfolio_cli
from axe_core import trace as trace_mod


@dataclass
class _FakeArtifacts:
    normalized_csv_path: Path
    weekly_review_path: Path
    position_table: list
    unified_sector_allocation: dict
    spy_comparison: dict
    hishtalmut_status: dict


def test_cli_emits_trace_success(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)

    fake = _FakeArtifacts(
        normalized_csv_path=tmp_path / "norm.csv",
        weekly_review_path=tmp_path / "weekly.json",
        position_table=[{"ticker": "MSFT"}, {"ticker": "GOOG"}],
        unified_sector_allocation={"Tech": 0.5},
        spy_comparison={"ytd": 0.03},
        hishtalmut_status={"ok": True},
    )
    monkeypatch.setattr(portfolio_cli, "run_portfolio_review", lambda: fake)

    portfolio_cli.main()

    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert index["runs"][0]["agent"] == "axe_portfolio"
    assert index["runs"][0]["status"] == "success"
    assert index["runs"][0]["artifact_written"] == "portfolio.json"


def test_cli_records_failure(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)

    def boom():
        raise FileNotFoundError("IBKR CSV missing")

    monkeypatch.setattr(portfolio_cli, "run_portfolio_review", boom)

    try:
        portfolio_cli.main()
    except FileNotFoundError:
        pass

    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert index["runs"][0]["agent"] == "axe_portfolio"
    assert index["runs"][0]["status"] == "failed"
