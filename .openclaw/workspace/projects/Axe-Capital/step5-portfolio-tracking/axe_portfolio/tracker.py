from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from axe_portfolio.ibkr import fetch_ibkr_portfolio
from axe_portfolio.util import axe_root, now_utc_iso, project_root, safe_float as _safe_float, today_local_iso

DATA_DIR_CANDIDATES = [
    axe_root() / "dashboard" / "data",
]
PREFERRED_DATA_DIR = axe_root() / "dashboard" / "data"
NORMALIZED_OUTPUT_PATH = PREFERRED_DATA_DIR / "portfolio_latest.normalized.csv"
WEEKLY_REVIEW_PATH = project_root() / "reports" / "weekly-review-latest.json"
INVESTOR_PROFILE_PATH = axe_root() / "INVESTOR_PROFILE.md"
DASHBOARD_JSON_PATH = axe_root() / "step6-dashboard" / "public" / "portfolio.json"

NORMALIZED_HEADER = {
    "symbol",
    "position",
    "last",
    "change_pct",
    "avg_price",
    "cost_basis",
    "market_value",
    "unrealized_pl",
    "unrealized_pl_pct",
    "pe",
    "eps_current",
}
RAW_HEADER = {
    "Financial Instrument",
    "Position",
    "Last",
    "Avg Price",
    "Cost Basis",
    "Market Value",
}

SECTOR_MAP = {
    "AMZN": "US Large Cap Tech",
    "ASML": "US Large Cap Tech",
    "FICO": "Software",
    "GOOG": "US Large Cap Tech",
    "IGV": "Software",
    "JPM": "Financials",
    "META": "US Large Cap Tech",
    "MSFT": "US Large Cap Tech",
    "QQQ": "US Large Cap Tech",
    "RGTI": "Space / Deep Tech",
    "RKLB": "Space / Deep Tech",
    "TSLA": "EV",
    "UBER": "Transportation",
    "Cash": "Cash",
}

PASSIVE_ACCOUNT_SECTOR_EXPOSURE = {
    "US Large Cap Tech": 60.0,
    "Financials": 4.0,
    "Software": 2.0,
    "Transportation": 5.0,
    "Space / Deep Tech": 4.0,
    "EV": 1.0,
    "S&P 500 broad": 40.0,
}


@dataclass
class ReviewArtifacts:
    normalized_csv_path: Path
    weekly_review_path: Path
    normalized_rows: list[dict[str, Any]]
    position_table: list[dict[str, Any]]
    unified_sector_allocation: list[dict[str, Any]]
    spy_comparison: dict[str, Any]
    hishtalmut_status: dict[str, Any]
    weekly_review: dict[str, Any]
    dashboard_json_path: Path


@dataclass
class PortfolioInput:
    kind: str
    path: Path
    rows: list[dict[str, Any]]
    cash: float


def _parse_hishtalmut_from_profile(path: Path = INVESTOR_PROFILE_PATH) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"annual_ceiling_ils": 21500, "deployed_2026_ils": 0, "remaining_2026_ils": 0}
    ceiling_match = re.search(r"Annual ceiling: ₪([0-9,]+)", text)
    remaining_match = re.search(r"2026 remaining contribution room: \*\*₪([0-9,]+)\*\*", text)
    annual_ceiling = int((ceiling_match.group(1) if ceiling_match else "21500").replace(",", ""))
    remaining = int((remaining_match.group(1) if remaining_match else "0").replace(",", ""))
    deployed = annual_ceiling - remaining
    return {
        "annual_ceiling_ils": annual_ceiling,
        "deployed_2026_ils": deployed,
        "remaining_2026_ils": remaining,
    }


def _available_data_dirs() -> list[Path]:
    existing = [path for path in DATA_DIR_CANDIDATES if path.exists()]
    return existing or [PREFERRED_DATA_DIR]


def _preferred_data_dir() -> Path:
    for path in _available_data_dirs():
        if path.name == "data" and path.parent.name == "dashboard":
            return path
    return _available_data_dirs()[0]


def _read_header(path: Path) -> set[str]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            return {str(col).strip() for col in header if str(col).strip()}
    except Exception:
        return set()


def _candidate_paths(filenames: list[str], *, include_raw_subdir: bool) -> list[Path]:
    paths: list[Path] = []
    for data_dir in _available_data_dirs():
        roots = [data_dir / "raw"] if include_raw_subdir else [data_dir]
        for root in roots:
            for filename in filenames:
                paths.append(root / filename)
    return paths


def _discover_by_header(required_header: set[str]) -> Path | None:
    for data_dir in _available_data_dirs():
        for root in [data_dir, data_dir / "raw"]:
            if not root.exists():
                continue
            for path in sorted(root.glob("*.csv")):
                header = _read_header(path)
                if required_header.issubset(header):
                    return path
    return None


def _resolve_normalized_source() -> Path | None:
    filenames = [
        "portfolio_latest.normalized.csv",
        "portfolio_latest_normalized.csv",
        "portfolio.normalized.csv",
        "portfolio_normalized.csv",
    ]
    for path in _candidate_paths(filenames, include_raw_subdir=False):
        if path.exists() and NORMALIZED_HEADER.issubset(_read_header(path)):
            return path
    return _discover_by_header(NORMALIZED_HEADER)


def _resolve_raw_source() -> Path | None:
    filenames = [
        "portfolio-current.csv",
        "portfolio_current.csv",
        "portfolio-latest.csv",
        "portfolio_latest.csv",
    ]
    for path in _candidate_paths(filenames, include_raw_subdir=True):
        if path.exists() and RAW_HEADER.issubset(_read_header(path)):
            return path
    return _discover_by_header(RAW_HEADER)


def _normalize_row(symbol: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "position": _safe_float(row.get("position") if "position" in row else row.get("Position")),
        "last": _safe_float(row.get("last") if "last" in row else row.get("Last")),
        "change_pct": _safe_float(row.get("change_pct") if "change_pct" in row else row.get("Change %")),
        "avg_price": _safe_float(row.get("avg_price") if "avg_price" in row else row.get("Avg Price")),
        "cost_basis": _safe_float(row.get("cost_basis") if "cost_basis" in row else row.get("Cost Basis")),
        "market_value": _safe_float(row.get("market_value") if "market_value" in row else row.get("Market Value")),
        "unrealized_pl": _safe_float(row.get("unrealized_pl") if "unrealized_pl" in row else row.get("Unrealized P&L")),
        "unrealized_pl_pct": _safe_float(row.get("unrealized_pl_pct") if "unrealized_pl_pct" in row else row.get("Unrealized P&L %")),
        "pe": _safe_float(row.get("pe") if "pe" in row else row.get("P/E")),
        "eps_current": _safe_float(row.get("eps_current") if "eps_current" in row else row.get("EPS (current)")),
    }


def _load_raw_portfolio_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
    return rows


def normalize_raw_portfolio(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        symbol = (row.get("Financial Instrument") or "").strip()
        if symbol in {"", "Total", "Cash"}:
            continue
        normalized.append(_normalize_row(symbol, row))
    return normalized


def _load_normalized_portfolio_csv(path: Path) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = (row.get("symbol") or row.get("Symbol") or "").strip()
            if symbol in {"", "Total", "Cash"}:
                continue
            normalized.append(_normalize_row(symbol, row))
    return normalized


def _read_cash_from_raw(path: Path | None) -> float:
    if path is None:
        return 0.0
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                sym = (row.get("Financial Instrument") or "").strip()
                if sym == "Cash":
                    return _safe_float(row.get("Market Value")) or 0.0
    except Exception:
        pass
    return 0.0


def _read_cash_from_existing_dashboard() -> float:
    try:
        data = json.loads(DASHBOARD_JSON_PATH.read_text(encoding="utf-8"))
        return float(data.get("summary", {}).get("cash", 0.0) or 0.0)
    except Exception:
        return 0.0


def _resolve_portfolio_input() -> PortfolioInput:
    source = os.getenv("AXE_PORTFOLIO_SOURCE", "csv").strip().lower()
    if source not in {"csv", "ibkr", "auto"}:
        raise ValueError("AXE_PORTFOLIO_SOURCE must be one of: csv, ibkr, auto")

    if source in {"ibkr", "auto"}:
        try:
            rows, cash = fetch_ibkr_portfolio()
        except Exception:
            if source == "ibkr":
                raise
        else:
            if rows:
                return PortfolioInput(kind="ibkr", path=Path("ibkr://live"), rows=rows, cash=cash)
            if source == "ibkr":
                raise RuntimeError("IBKR connection succeeded, but no portfolio positions were returned.")

    normalized_source = _resolve_normalized_source()
    if normalized_source is not None:
        return PortfolioInput(
            kind="normalized",
            path=normalized_source,
            rows=_load_normalized_portfolio_csv(normalized_source),
            cash=_read_cash_from_existing_dashboard(),
        )

    raw_source = _resolve_raw_source()
    if raw_source is not None:
        raw_rows = _load_raw_portfolio_csv(raw_source)
        return PortfolioInput(
            kind="raw",
            path=raw_source,
            rows=normalize_raw_portfolio(raw_rows),
            cash=_read_cash_from_raw(raw_source),
        )

    searched = [str(path) for path in _candidate_paths([
        "portfolio_latest.normalized.csv",
        "portfolio_latest_normalized.csv",
        "portfolio.normalized.csv",
        "portfolio_normalized.csv",
    ], include_raw_subdir=False)]
    searched.extend(
        str(path)
        for path in _candidate_paths([
            "portfolio-current.csv",
            "portfolio_current.csv",
            "portfolio-latest.csv",
            "portfolio_latest.csv",
        ], include_raw_subdir=True)
    )
    raise FileNotFoundError(
        "No portfolio CSV found. Checked normalized and raw candidates under dashboard/data: "
        + ", ".join(searched)
    )


def write_normalized_csv(rows: list[dict[str, Any]], path: Path = NORMALIZED_OUTPUT_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        rows,
        columns=[
            "symbol",
            "position",
            "last",
            "change_pct",
            "avg_price",
            "cost_basis",
            "market_value",
            "unrealized_pl",
            "unrealized_pl_pct",
            "pe",
            "eps_current",
        ],
    )
    df.to_csv(path, index=False)
    return path


def _alert_status(distance_to_stop_pct: float) -> str:
    if distance_to_stop_pct < 5:
        return "RED"
    if distance_to_stop_pct <= 10:
        return "YELLOW"
    return "GREEN"


def build_position_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_nav = sum((row.get("market_value") or 0.0) for row in rows)
    table: list[dict[str, Any]] = []
    for row in rows:
        avg_price = row.get("avg_price") or 0.0
        last = row.get("last") or 0.0
        stop_loss_level = round(avg_price * 0.90, 2)
        distance_to_stop_pct = round(((last - stop_loss_level) / last) * 100, 2) if last else None
        sector = SECTOR_MAP.get(row["symbol"], "Other")
        weight_pct = round(((row.get("market_value") or 0.0) / total_nav) * 100, 2) if total_nav else 0.0
        table.append(
            {
                **row,
                "stop_loss_level": stop_loss_level,
                "distance_to_stop_pct": distance_to_stop_pct,
                "sector_tag": sector,
                "weight_pct": weight_pct,
                "alert_status": _alert_status(distance_to_stop_pct or 0.0),
            }
        )
    return table


def build_unified_sector_allocation(position_table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ibkr_total = sum((row.get("market_value") or 0.0) for row in position_table)
    ibkr_sector_values: dict[str, float] = {}
    for row in position_table:
        sector = row["sector_tag"]
        ibkr_sector_values[sector] = ibkr_sector_values.get(sector, 0.0) + (row.get("market_value") or 0.0)

    ibkr_sector_pct = {
        sector: round((value / ibkr_total) * 100 if ibkr_total else 0.0, 2)
        for sector, value in ibkr_sector_values.items()
    }

    sectors = sorted(set(PASSIVE_ACCOUNT_SECTOR_EXPOSURE) | set(ibkr_sector_pct))
    allocation = []
    for sector in sectors:
        ibkr_pct = ibkr_sector_pct.get(sector, 0.0)
        passive_pct = round(PASSIVE_ACCOUNT_SECTOR_EXPOSURE.get(sector, 0.0), 2)
        allocation.append({"sector": sector, "ibkr_pct": ibkr_pct, "passive_pct": passive_pct})
    allocation.sort(key=lambda x: x["ibkr_pct"], reverse=True)
    return allocation


def compute_spy_comparison(position_table: list[dict[str, Any]]) -> dict[str, Any]:
    total_cost = sum((row.get("cost_basis") or 0.0) for row in position_table)
    total_market = sum((row.get("market_value") or 0.0) for row in position_table)
    portfolio_return_pct = round(((total_market / total_cost) - 1) * 100, 2) if total_cost else 0.0

    spy = yf.Ticker("SPY")
    hist = spy.history(period="1y", interval="1d", auto_adjust=False)
    latest = float(hist.iloc[-1]["Close"])
    first = float(hist.iloc[0]["Close"])
    spy_return_pct = round(((latest / first) - 1) * 100, 2) if first else 0.0
    relative_alpha_pct = round(portfolio_return_pct - spy_return_pct, 2)

    return {
        "portfolio_cost_basis": round(total_cost, 2),
        "portfolio_market_value": round(total_market, 2),
        "portfolio_return_pct": portfolio_return_pct,
        "spy_return_pct_same_window": spy_return_pct,
        "relative_alpha_pct": relative_alpha_pct,
    }


def build_hishtalmut_status() -> dict[str, Any]:
    status = _parse_hishtalmut_from_profile()
    remaining = status["remaining_2026_ils"]
    return {**status, "priority": remaining > 0, "status": "PRIORITY" if remaining > 0 else "MAXED"}


def build_weekly_review(
    position_table: list[dict[str, Any]],
    unified_sector_allocation: list[dict[str, Any]],
    spy_comparison: dict[str, Any],
    hishtalmut_status: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at": now_utc_iso(),
        "review_date": today_local_iso(),
        "positions": [
            {
                "symbol": row["symbol"],
                "market_value": row["market_value"],
                "unrealized_pl": row["unrealized_pl"],
                "unrealized_pl_pct": row["unrealized_pl_pct"],
                "stop_loss_level": row["stop_loss_level"],
                "distance_to_stop_pct": row["distance_to_stop_pct"],
                "alert_status": row["alert_status"],
                "sector_tag": row["sector_tag"],
                "weight_pct": row["weight_pct"],
            }
            for row in position_table
        ],
        "sector_concentration": unified_sector_allocation,
        "spy_comparison": spy_comparison,
        "hishtalmut_status": hishtalmut_status,
    }


def write_weekly_review(review: dict[str, Any], path: Path = WEEKLY_REVIEW_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_dashboard_json(
    position_table: list[dict[str, Any]],
    unified_sector_allocation: list[dict[str, Any]],
    hishtalmut_status: dict[str, Any],
    review_date: str,
    cash: float,
) -> dict[str, Any]:
    positions_value = sum((row.get("market_value") or 0.0) for row in position_table)
    nav = round(positions_value + cash, 2)
    cash_pct = round((cash / nav) * 100, 1) if nav else 0.0
    total_upl = sum((row.get("unrealized_pl") or 0.0) for row in position_table)
    total_cost = sum((row.get("cost_basis") or 0.0) for row in position_table)
    total_upl_pct = round((total_upl / total_cost * 100) if total_cost else 0.0, 2)
    alert_order = {"RED": 0, "YELLOW": 1, "GREEN": 2}
    sorted_positions = sorted(position_table, key=lambda x: alert_order.get(x.get("alert_status", "GREEN"), 2))
    return {
        "generated_at": now_utc_iso(),
        "review_date": review_date,
        "positions": [{**row, "shares": row.get("position"), "last_price": row.get("last")} for row in sorted_positions],
        "summary": {
            "nav": nav,
            "positions_value": round(positions_value, 2),
            "cash": round(cash, 2),
            "cash_pct": cash_pct,
            "total_unrealized_pl": round(total_upl, 2),
            "total_unrealized_pl_pct": total_upl_pct,
            "red_count": sum(1 for r in position_table if r.get("alert_status") == "RED"),
            "yellow_count": sum(1 for r in position_table if r.get("alert_status") == "YELLOW"),
            "green_count": sum(1 for r in position_table if r.get("alert_status") == "GREEN"),
        },
        "sector_weights": unified_sector_allocation,
        "hishtalmut": hishtalmut_status,
    }


def write_dashboard_json(dashboard: dict[str, Any], path: Path = DASHBOARD_JSON_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_portfolio_review() -> ReviewArtifacts:
    portfolio_input = _resolve_portfolio_input()
    normalized_rows = portfolio_input.rows
    normalized_csv_path = write_normalized_csv(normalized_rows, path=_preferred_data_dir() / "portfolio_latest.normalized.csv")
    position_table = build_position_table(normalized_rows)
    unified_sector_allocation = build_unified_sector_allocation(position_table)
    spy_comparison = compute_spy_comparison(position_table)
    hishtalmut_status = build_hishtalmut_status()
    weekly_review = build_weekly_review(position_table, unified_sector_allocation, spy_comparison, hishtalmut_status)
    weekly_review_path = write_weekly_review(weekly_review)
    dashboard = build_dashboard_json(
        position_table,
        unified_sector_allocation,
        hishtalmut_status,
        weekly_review["review_date"],
        cash=portfolio_input.cash,
    )
    write_dashboard_json(dashboard)
    return ReviewArtifacts(
        normalized_csv_path=normalized_csv_path,
        weekly_review_path=weekly_review_path,
        normalized_rows=normalized_rows,
        position_table=position_table,
        unified_sector_allocation=unified_sector_allocation,
        spy_comparison=spy_comparison,
        hishtalmut_status=hishtalmut_status,
        weekly_review=weekly_review,
        dashboard_json_path=DASHBOARD_JSON_PATH,
    )
