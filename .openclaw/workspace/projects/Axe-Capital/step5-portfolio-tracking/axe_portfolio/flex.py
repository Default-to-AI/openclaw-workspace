from __future__ import annotations

import os
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import requests

_SEND_URL = "https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"
_GET_URL = "https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement"
_MAX_RETRIES = 10
_RETRY_SLEEP = 3.0
_SKIP_ASSET_CATEGORIES = {"CASH", "BAG", "FXCFD"}


@dataclass
class FlexQueryConfig:
    token: str
    query_id: str
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> "FlexQueryConfig":
        token = os.getenv("AXE_IBKR_FLEX_TOKEN", "").strip()
        query_id = os.getenv("AXE_IBKR_FLEX_QUERY_ID", "").strip()
        if not token or not query_id:
            raise RuntimeError(
                "Flex Query requires AXE_IBKR_FLEX_TOKEN and AXE_IBKR_FLEX_QUERY_ID in .env. "
                "Set them in IBKR Account Management → Reports → Flex Queries."
            )
        return cls(token=token, query_id=query_id)


def _parse_send_response(xml_text: str) -> str:
    root = ET.fromstring(xml_text)
    status = root.findtext("Status", "")
    if status != "Success":
        code = root.findtext("ErrorCode", "unknown")
        msg = root.findtext("ErrorMessage", "no message")
        raise RuntimeError(f"Flex Query SendRequest failed (code {code}): {msg}")
    ref = root.findtext("ReferenceCode", "")
    if not ref:
        raise RuntimeError("Flex Query SendRequest returned Success but no ReferenceCode")
    return ref


def _request_statement(config: FlexQueryConfig) -> str:
    resp = requests.get(
        _SEND_URL,
        params={"t": config.token, "q": config.query_id, "v": "3"},
        timeout=config.timeout,
    )
    resp.raise_for_status()
    return _parse_send_response(resp.text)


def _fetch_statement(ref_code: str, config: FlexQueryConfig) -> str:
    for attempt in range(_MAX_RETRIES):
        resp = requests.get(
            _GET_URL,
            params={"q": ref_code, "t": config.token, "v": "3"},
            timeout=config.timeout,
        )
        resp.raise_for_status()
        text = resp.text
        if "Statement generation in progress" in text:
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_SLEEP)
                continue
            raise TimeoutError(
                f"Flex Query statement still pending after {_MAX_RETRIES} retries ({_MAX_RETRIES * _RETRY_SLEEP:.0f}s)"
            )
        return text
    raise TimeoutError(f"Flex Query statement still pending after {_MAX_RETRIES} retries")


def _aggregate_by_symbol(rows: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in rows:
        symbol = row["symbol"]
        if symbol not in seen:
            seen[symbol] = dict(row)
            continue
        existing = seen[symbol]
        existing["position"] += row["position"]
        existing["cost_basis"] += row["cost_basis"]
        existing["unrealized_pl"] += row["unrealized_pl"]
        existing["market_value"] = round(existing["market_value"] + row["market_value"], 2)
        pos = existing["position"]
        cb = existing["cost_basis"]
        existing["avg_price"] = round(cb / pos, 6) if pos else 0.0
        existing["unrealized_pl_pct"] = round((existing["unrealized_pl"] / cb) * 100, 2) if cb else 0.0
    return list(seen.values())


def _parse_statement(xml_text: str) -> tuple[list[dict], float]:
    root = ET.fromstring(xml_text)

    rows: list[dict] = []
    for pos in root.iter("OpenPosition"):
        if pos.attrib.get("assetCategory", "") in _SKIP_ASSET_CATEGORIES:
            continue
        symbol = pos.attrib.get("symbol", "")
        position = float(pos.attrib.get("position", 0))
        last = float(pos.attrib.get("markPrice", 0))
        avg_price = float(pos.attrib.get("costBasisPrice", 0))
        cost_basis = float(pos.attrib.get("costBasisMoney", 0))
        unrealized_pl = float(pos.attrib.get("fifoPnlUnrealized", 0))
        market_value = round(position * last, 2)
        unrealized_pl_pct = round((unrealized_pl / cost_basis) * 100, 2) if cost_basis else 0.0
        rows.append({
            "symbol": symbol,
            "position": position,
            "last": last,
            "avg_price": avg_price,
            "cost_basis": cost_basis,
            "unrealized_pl": unrealized_pl,
            "unrealized_pl_pct": unrealized_pl_pct,
            "market_value": market_value,
            "change_pct": None,
            "pe": None,
            "eps_current": None,
        })

    rows = _aggregate_by_symbol(rows)

    # Cash priority: BASE (authoritative total) → USD only → sum all (no currency attr).
    # BASE and USD are the same money viewed differently; never double-count them.
    base_cash: list[float] = []
    usd_cash: list[float] = []
    all_cash: list[float] = []
    has_currency_attr = False
    for cash_el in root.iter("CashReportCurrency"):
        ending = float(cash_el.attrib.get("endingCash", 0) or 0)
        currency = cash_el.attrib.get("currency", "")
        all_cash.append(ending)
        if currency:
            has_currency_attr = True
            if currency == "BASE":
                base_cash.append(ending)
            elif currency == "USD":
                usd_cash.append(ending)

    if base_cash:
        cash = sum(base_cash)
    elif has_currency_attr:
        cash = sum(usd_cash)
    else:
        cash = sum(all_cash)

    return rows, cash


def fetch_flex_portfolio(config: FlexQueryConfig | None = None) -> tuple[list[dict], float]:
    if config is None:
        config = FlexQueryConfig.from_env()
    ref_code = _request_statement(config)
    xml_text = _fetch_statement(ref_code, config)
    rows, cash = _parse_statement(xml_text)
    if not rows:
        raise RuntimeError("Flex Query returned no positions")
    return rows, cash
