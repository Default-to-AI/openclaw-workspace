"""Thin wrappers that invoke each agent's CLI. Return codes are failure counts."""
from __future__ import annotations

import json
import os
import subprocess
import sys

from axe_core.paths import project_root, public_dir


RUN_ALL_ORDER = ("portfolio", "alpha", "news")
AGENT_ORDER = (
    "portfolio",
    "alpha",
    "news",
    "specialists",
    "specialists_decide",
    "opportunities",
    "fundamental",
    "technical",
    "macro",
    "decision",
)


_MODULE_TIMEOUTS: dict[str, int] = {
    "axe_portfolio.cli": 120,  # connect(10s) + poll-until-data(≤8s×2 accts) + yfinance + margin
}
_DEFAULT_TIMEOUT = 300


def _run_module(module: str, cwd_subdir: str, *args: str) -> int:
    cwd = project_root() / cwd_subdir
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    timeout = _MODULE_TIMEOUTS.get(module, _DEFAULT_TIMEOUT)
    try:
        result = subprocess.run(
            [sys.executable, "-m", module, *args],
            check=False,
            cwd=cwd,
            env=env,
            timeout=timeout,
        )
        return 0 if result.returncode == 0 else 1
    except subprocess.TimeoutExpired:
        print(f"[axe] {module} exceeded timeout ({timeout}s); killed", file=sys.stderr)
        return 1


def run_alpha() -> int:
    return _run_module("axe_alpha.cli", "step4-alpha-hunter")


def run_portfolio() -> int:
    return _run_module("axe_portfolio.cli", "step5-portfolio-tracking")


def run_news() -> int:
    return _run_module("axe_news.cli", "step2-news")


def run_fundamental(ticker: str) -> int:
    return _run_module("axe_fundamental.cli", "step8-fundamental", ticker.upper())


def run_technical(ticker: str) -> int:
    return _run_module("axe_technical.cli", "step9-technical", ticker.upper())


def run_macro(ticker: str) -> int:
    return _run_module("axe_macro.cli", "step10-macro", ticker.upper())


def run_decision(ticker: str | None = None) -> int:
    return _run_module("axe_decision.cli", "step3-debate-decision", (ticker or "MSFT").upper())


def portfolio_symbols() -> list[str]:
    path = public_dir() / "portfolio.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    symbols: list[str] = []
    for position in data.get("positions", []):
        symbol = str(position.get("symbol") or "").strip().upper()
        if not symbol or symbol == "CASH":
            continue
        quantity = position.get("position", position.get("shares", 0))
        try:
            quantity_float = float(quantity or 0)
        except (TypeError, ValueError):
            quantity_float = 0.0
        if quantity_float <= 0:
            continue
        if symbol not in symbols:
            symbols.append(symbol)
    return symbols


def opportunity_tickers(limit: int = 2) -> list[str]:
    alpha_path = public_dir() / "alpha-latest.json"
    data = json.loads(alpha_path.read_text(encoding="utf-8"))
    held = set(portfolio_symbols())
    tickers: list[str] = []
    for opportunity in data.get("top_opportunities", []):
        symbol = str(opportunity.get("ticker") or "").strip().upper()
        if not symbol or symbol in held or symbol in tickers:
            continue
        tickers.append(symbol)
        if len(tickers) >= limit:
            break
    return tickers


def run_specialists(ticker: str | None = None) -> int:
    """Run fundamental/technical/macro for a single ticker or all portfolio symbols."""
    portfolio_rc = run_portfolio()
    if portfolio_rc != 0:
        return portfolio_rc
    failures = 0
    symbols = [ticker.upper()] if ticker else portfolio_symbols()
    if not symbols:
        return 1
    for symbol in symbols:
        failures += run_fundamental(symbol)
        failures += run_technical(symbol)
        failures += run_macro(symbol)
    return 0 if failures == 0 else failures


def run_specialists_and_decide(ticker: str | None = None) -> int:
    """Run specialists then immediately run the decision memo for each symbol."""
    rc = run_specialists(ticker)
    if rc != 0:
        return rc
    symbols = [ticker.upper()] if ticker else portfolio_symbols()
    failures = 0
    for symbol in symbols:
        failures += run_decision(symbol)
    return 0 if failures == 0 else failures


def run_opportunities(limit: str | int | None = None) -> int:
    try:
        count = int(limit) if limit is not None else 2
    except (TypeError, ValueError):
        count = 2
    if count < 1:
        count = 1

    portfolio_rc = run_portfolio()
    if portfolio_rc != 0:
        return portfolio_rc
    alpha_rc = run_alpha()
    if alpha_rc != 0:
        return alpha_rc

    symbols = opportunity_tickers(limit=count)
    if not symbols:
        return 1

    failures = 0
    for symbol in symbols:
        failures += run_fundamental(symbol)
        failures += run_technical(symbol)
        failures += run_macro(symbol)
        failures += run_decision(symbol)
    return 0 if failures == 0 else failures


def run_all() -> dict[str, int]:
    return {
        "portfolio": run_portfolio(),
        "alpha": run_alpha(),
        "news": run_news(),
    }
