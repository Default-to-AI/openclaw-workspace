from __future__ import annotations
from axe_portfolio.tracker import build_position_table, SECTOR_MAP


def test_nflx_has_sector():
    assert "NFLX" in SECTOR_MAP
    assert SECTOR_MAP["NFLX"] != "Other"


def test_build_position_table_nflx_sector():
    rows = [
        {
            "symbol": "NFLX",
            "position": 20.0,
            "last": 100.0,
            "change_pct": None,
            "avg_price": 97.44,
            "cost_basis": 1948.80,
            "market_value": 2000.0,
            "unrealized_pl": 51.20,
            "unrealized_pl_pct": 2.63,
            "pe": None,
            "eps_current": None,
        }
    ]
    table = build_position_table(rows)
    assert table[0]["sector_tag"] == "Streaming"
