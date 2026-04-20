from __future__ import annotations

from unittest.mock import patch

from axe_portfolio.tracker import _resolve_portfolio_input


FAKE_ROWS = [
    {
        "symbol": "TSLA",
        "position": 50.0,
        "last": 170.0,
        "change_pct": None,
        "avg_price": 155.0,
        "cost_basis": 7750.0,
        "market_value": 8500.0,
        "unrealized_pl": 750.0,
        "unrealized_pl_pct": 9.68,
        "pe": None,
        "eps_current": None,
    }
]
FAKE_CASH = 9253.0


def test_flex_fallback_when_ibkr_fails(monkeypatch):
    monkeypatch.setenv("AXE_PORTFOLIO_SOURCE", "auto")
    with patch("axe_portfolio.tracker.fetch_ibkr_portfolio", side_effect=ConnectionRefusedError("TWS offline")):
        with patch("axe_portfolio.tracker.fetch_flex_portfolio", return_value=(FAKE_ROWS, FAKE_CASH)):
            result = _resolve_portfolio_input()
    assert result.kind == "flex"
    assert result.cash == FAKE_CASH
    assert result.rows[0]["symbol"] == "TSLA"
