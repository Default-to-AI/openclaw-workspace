"""Resolve the current watchlist (held + interesting tickers) from INVESTOR_PROFILE.md."""
from __future__ import annotations

import re

from axe_core.paths import project_root


def load_watchlist() -> set[str]:
    text = (project_root() / "INVESTOR_PROFILE.md").read_text(encoding="utf-8")
    tickers: set[str] = set()
    in_holdings = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "### IBKR Holdings — Current Positions":
            in_holdings = True
            continue
        if in_holdings and stripped.startswith("**IBKR NAV**"):
            in_holdings = False
        if in_holdings and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells and re.fullmatch(r"[A-Z]{1,5}", cells[0] or ""):
                tickers.add(cells[0])
    # Fallback minimum set if the profile hasn't been parsed yet.
    if not tickers:
        tickers = {"MSFT", "GOOG", "AAPL", "NVDA", "RTX", "ASML", "SPY", "QQQ"}
    return tickers
