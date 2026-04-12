from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yfinance as yf

from axe_coo.models import FinancialSnapshot, PriceHistory


@dataclass
class YFinanceResult:
    prices: PriceHistory | None
    snapshot: FinancialSnapshot | None
    earnings_dates: list[str]


def _safe_float(x: Any) -> float | None:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def fetch_yfinance_bundle(ticker: str, period: str = "6mo", interval: str = "1d") -> YFinanceResult:
    t = yf.Ticker(ticker)

    hist = None
    try:
        df = t.history(period=period, interval=interval, auto_adjust=False)
        rows: list[dict[str, Any]] = []
        if df is not None and len(df) > 0:
            for idx, row in df.iterrows():
                ts = idx.to_pydatetime().isoformat()
                rows.append(
                    {
                        "ts": ts,
                        "open": _safe_float(row.get("Open")),
                        "high": _safe_float(row.get("High")),
                        "low": _safe_float(row.get("Low")),
                        "close": _safe_float(row.get("Close")),
                        "volume": _safe_float(row.get("Volume")),
                    }
                )
        hist = PriceHistory(interval=interval, period=period, rows=rows, currency=None)
    except Exception:
        hist = None

    info = {}
    try:
        info = t.get_info() or {}
    except Exception:
        info = {}

    snap = FinancialSnapshot(
        currency=info.get("currency"),
        market_cap=_safe_float(info.get("marketCap")),
        shares_outstanding=_safe_float(info.get("sharesOutstanding")),
        trailing_pe=_safe_float(info.get("trailingPE")),
        forward_pe=_safe_float(info.get("forwardPE")),
        price_to_book=_safe_float(info.get("priceToBook")),
        profit_margins=_safe_float(info.get("profitMargins")),
        operating_margins=_safe_float(info.get("operatingMargins")),
        return_on_equity=_safe_float(info.get("returnOnEquity")),
        total_cash=_safe_float(info.get("totalCash")),
        total_debt=_safe_float(info.get("totalDebt")),
        free_cashflow=_safe_float(info.get("freeCashflow")),
        revenue_ttm=_safe_float(info.get("totalRevenue")),
    )

    earnings_dates: list[str] = []
    try:
        ed = t.earnings_dates
        if ed is not None and len(ed) > 0:
            # index is timestamp
            for idx in ed.index[:10]:
                try:
                    earnings_dates.append(idx.to_pydatetime().date().isoformat())
                except Exception:
                    pass
    except Exception:
        pass

    return YFinanceResult(prices=hist, snapshot=snap, earnings_dates=earnings_dates)
