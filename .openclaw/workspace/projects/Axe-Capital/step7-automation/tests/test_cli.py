from __future__ import annotations

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

    def fake_run(cmd, check, cwd):
        captured["cmd"] = cmd
        captured["cwd"] = str(cwd)

        class R:
            returncode = 0

        return R()

    import subprocess

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert runners.run_alpha() == 0
    assert captured["cmd"][0:2] == [sys.executable, "-m"]
    assert "axe_alpha.cli" in captured["cmd"][2]
