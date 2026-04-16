from __future__ import annotations

import json
import sys

from axe_orchestrator import cli, runners


def test_run_alpha_calls_alpha_runner(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(runners, "run_alpha", lambda: calls.append("alpha") or 0)
    exit_code = cli.main(["run", "alpha"])
    assert calls == ["alpha"]
    assert exit_code == 0


def test_run_all_invokes_every_agent_even_if_one_fails(monkeypatch):
    order = []

    def ok(name):
        def _r():
            order.append(name)
            return 0
        return _r

    def bad(name):
        def _r():
            order.append(name)
            return 1
        return _r

    monkeypatch.setattr(runners, "run_portfolio", ok("portfolio"))
    monkeypatch.setattr(runners, "run_alpha", bad("alpha"))
    monkeypatch.setattr(runners, "run_news", ok("news"))

    exit_code = cli.main(["run", "all"])

    assert order == ["portfolio", "alpha", "news"]
    assert exit_code == 1


def test_unknown_target_returns_nonzero(monkeypatch, capsys):
    assert cli.main(["run", "bogus"]) != 0


def test_runners_shell_out(monkeypatch):
    captured = {}

    def fake_run(cmd, check, cwd, env):
        captured["cmd"] = cmd
        captured["cwd"] = str(cwd)
        captured["env"] = env

        class R:
            returncode = 0

        return R()

    import subprocess

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert runners.run_alpha() == 0
    assert captured["cmd"][0:2] == [sys.executable, "-m"]
    assert "axe_alpha.cli" in captured["cmd"][2]
    assert captured["env"]["PYTHONUNBUFFERED"] == "1"


def test_portfolio_symbols_come_from_positive_positions(tmp_path, monkeypatch):
    portfolio = {
        "positions": [
            {"symbol": "GOOG", "position": 5},
            {"symbol": "QQQ", "shares": 2},
            {"symbol": "CASH", "position": 100},
            {"symbol": "MSFT", "position": 0},
            {"symbol": "", "position": 1},
        ]
    }
    public = tmp_path / "public"
    public.mkdir()
    (public / "portfolio.json").write_text(json.dumps(portfolio), encoding="utf-8")
    monkeypatch.setattr(runners, "public_dir", lambda: public)

    assert runners.portfolio_symbols() == ["GOOG", "QQQ"]


def test_run_decision_accepts_ticker_argument(monkeypatch):
    captured = {}

    def fake_run(cmd, check, cwd, env):
        captured["cmd"] = cmd

        class R:
            returncode = 0

        return R()

    import subprocess

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert runners.run_decision("GOOG") == 0
    assert captured["cmd"][-1] == "GOOG"


def test_cli_passes_ticker_to_runner(monkeypatch):
    calls = []
    monkeypatch.setattr(runners, "run_decision", lambda ticker=None: calls.append(ticker) or 0)

    exit_code = cli.main(["run", "decision", "GOOG"])

    assert exit_code == 0
    assert calls == ["GOOG"]


def test_run_specialists_refreshes_portfolio_then_runs_all_agents(monkeypatch):
    calls = []
    monkeypatch.setattr(runners, "run_portfolio", lambda: calls.append("portfolio") or 0)
    monkeypatch.setattr(runners, "portfolio_symbols", lambda: ["GOOG", "QQQ"])
    monkeypatch.setattr(runners, "run_fundamental", lambda ticker: calls.append(("fundamental", ticker)) or 0)
    monkeypatch.setattr(runners, "run_technical", lambda ticker: calls.append(("technical", ticker)) or 0)
    monkeypatch.setattr(runners, "run_macro", lambda ticker: calls.append(("macro", ticker)) or 0)

    assert runners.run_specialists() == 0
    assert calls == [
        "portfolio",
        ("fundamental", "GOOG"),
        ("technical", "GOOG"),
        ("macro", "GOOG"),
        ("fundamental", "QQQ"),
        ("technical", "QQQ"),
        ("macro", "QQQ"),
    ]


def test_run_specialists_stops_if_portfolio_refresh_fails(monkeypatch):
    calls = []
    monkeypatch.setattr(runners, "run_portfolio", lambda: 1)
    monkeypatch.setattr(runners, "portfolio_symbols", lambda: calls.append("symbols") or ["GOOG"])

    assert runners.run_specialists() == 1
    assert calls == []


def test_opportunity_tickers_read_alpha_latest_excluding_portfolio(tmp_path, monkeypatch):
    public = tmp_path / "public"
    public.mkdir()
    (public / "portfolio.json").write_text(
        json.dumps({"positions": [{"symbol": "GOOG", "position": 1}]}),
        encoding="utf-8",
    )
    (public / "alpha-latest.json").write_text(
        json.dumps(
            {
                "top_opportunities": [
                    {"ticker": "GOOG", "conviction_score": 9},
                    {"ticker": "RTX", "conviction_score": 8},
                    {"ticker": "CVX", "conviction_score": 7},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(runners, "public_dir", lambda: public)

    assert runners.opportunity_tickers(limit=2) == ["RTX", "CVX"]


def test_run_opportunities_runs_alpha_specialists_and_decisions(monkeypatch):
    calls = []
    monkeypatch.setattr(runners, "run_portfolio", lambda: calls.append("portfolio") or 0)
    monkeypatch.setattr(runners, "run_alpha", lambda: calls.append("alpha") or 0)
    monkeypatch.setattr(runners, "opportunity_tickers", lambda limit=2: ["RTX", "CVX"])
    monkeypatch.setattr(runners, "run_fundamental", lambda ticker: calls.append(("fundamental", ticker)) or 0)
    monkeypatch.setattr(runners, "run_technical", lambda ticker: calls.append(("technical", ticker)) or 0)
    monkeypatch.setattr(runners, "run_macro", lambda ticker: calls.append(("macro", ticker)) or 0)
    monkeypatch.setattr(runners, "run_decision", lambda ticker: calls.append(("decision", ticker)) or 0)

    assert runners.run_opportunities("2") == 0
    assert calls == [
        "portfolio",
        "alpha",
        ("fundamental", "RTX"),
        ("technical", "RTX"),
        ("macro", "RTX"),
        ("decision", "RTX"),
        ("fundamental", "CVX"),
        ("technical", "CVX"),
        ("macro", "CVX"),
        ("decision", "CVX"),
    ]


def test_cli_runs_opportunities_with_limit(monkeypatch):
    calls = []
    monkeypatch.setattr(runners, "run_opportunities", lambda limit=None: calls.append(limit) or 0)

    assert cli.main(["run", "opportunities", "3"]) == 0
    assert calls == ["3"]
