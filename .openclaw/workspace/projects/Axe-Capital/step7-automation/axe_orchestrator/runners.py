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
    "opportunities",
    "fundamental",
    "technical",
    "macro",
    "decision",
)


def _run_module(module: str, cwd_subdir: str, *args: str) -> int:
    cwd = project_root() / cwd_subdir
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", module, *args],
        check=False,
        cwd=cwd,
        env=env,
    )
    return 0 if result.returncode == 0 else 1


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


def run_specialists() -> int:
    portfolio_rc = run_portfolio()
    if portfolio_rc != 0:
        return portfolio_rc
    failures = 0
    symbols = portfolio_symbols()
    if not symbols:
        return 1

    for symbol in symbols:
        failures += run_fundamental(symbol)
        failures += run_technical(symbol)
        failures += run_macro(symbol)
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
