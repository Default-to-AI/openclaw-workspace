from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from axe_portfolio.util import safe_float as _safe_float


@dataclass(frozen=True)
class IBKRConnectionConfig:
    host: str = "127.0.0.1"
    port: int = 7496
    client_id: int = 51
    account: str | None = None
    accounts: tuple[str, ...] | None = None
    timeout: float = 10.0
    readonly: bool = True

    @classmethod
    def from_env(cls) -> "IBKRConnectionConfig":
        accounts_env = (os.getenv("AXE_IBKR_ACCOUNTS") or "").strip()
        accounts: tuple[str, ...] | None = None
        if accounts_env:
            parsed = [part.strip() for part in accounts_env.split(",") if part.strip()]
            accounts = tuple(parsed) if parsed else None
        return cls(
            host=os.getenv("AXE_IBKR_HOST", "127.0.0.1"),
            port=int(os.getenv("AXE_IBKR_PORT", "7496")),
            client_id=int(os.getenv("AXE_IBKR_CLIENT_ID", "51")),
            account=os.getenv("AXE_IBKR_ACCOUNT") or None,
            accounts=accounts,
            timeout=float(os.getenv("AXE_IBKR_TIMEOUT", "10")),
            readonly=os.getenv("AXE_IBKR_READONLY", "1").lower() not in {"0", "false", "no"},
        )


def _require_ib_class() -> type:
    try:
        from ib_async import IB
    except ImportError as exc:
        raise RuntimeError(
            "ib_async is not installed. Install step5 dependencies, then run with "
            "AXE_PORTFOLIO_SOURCE=ibkr."
        ) from exc
    return IB


def _symbol_from_contract(contract: Any) -> str:
    local_symbol = str(getattr(contract, "localSymbol", "") or "").strip()
    symbol = str(getattr(contract, "symbol", "") or "").strip()
    return symbol or local_symbol


def _row_from_portfolio_item(item: Any) -> dict[str, Any] | None:
    contract = getattr(item, "contract", None)
    symbol = _symbol_from_contract(contract)
    if not symbol:
        return None
    sec_type = str(getattr(contract, "secType", "") or "").upper()
    if sec_type in {"CASH", "BAG"}:
        return None

    position = _safe_float(getattr(item, "position", None)) or 0.0
    last = _safe_float(getattr(item, "marketPrice", None)) or 0.0
    avg_price = _safe_float(getattr(item, "averageCost", None)) or 0.0
    market_value = _safe_float(getattr(item, "marketValue", None))
    if market_value is None:
        market_value = round(position * last, 2)
    cost_basis = round(position * avg_price, 2)
    unrealized_pl = _safe_float(getattr(item, "unrealizedPNL", None))
    if unrealized_pl is None:
        unrealized_pl = round(market_value - cost_basis, 2)
    unrealized_pl_pct = round((unrealized_pl / cost_basis) * 100, 2) if cost_basis else None

    return {
        "symbol": symbol,
        "position": position,
        "last": last,
        "change_pct": None,
        "avg_price": avg_price,
        "cost_basis": cost_basis,
        "market_value": round(market_value, 2),
        "unrealized_pl": round(unrealized_pl, 2),
        "unrealized_pl_pct": unrealized_pl_pct,
        "pe": None,
        "eps_current": None,
    }


def _row_from_position(position_item: Any) -> dict[str, Any] | None:
    contract = getattr(position_item, "contract", None)
    symbol = _symbol_from_contract(contract)
    if not symbol:
        return None
    sec_type = str(getattr(contract, "secType", "") or "").upper()
    if sec_type in {"CASH", "BAG"}:
        return None

    position = _safe_float(getattr(position_item, "position", None)) or 0.0
    avg_price = _safe_float(getattr(position_item, "avgCost", None)) or 0.0
    return {
        "symbol": symbol,
        "position": position,
        "last": avg_price,
        "change_pct": None,
        "avg_price": avg_price,
        "cost_basis": round(position * avg_price, 2),
        "market_value": round(position * avg_price, 2),
        "unrealized_pl": 0.0,
        "unrealized_pl_pct": 0.0,
        "pe": None,
        "eps_current": None,
    }


def _managed_accounts(ib: Any) -> list[str]:
    try:
        return [str(account).strip() for account in ib.managedAccounts() if str(account).strip()]
    except Exception:
        return []


def _resolve_accounts(ib: Any, cfg: IBKRConnectionConfig) -> list[str | None]:
    if cfg.accounts is not None:
        return list(cfg.accounts)
    if cfg.account:
        return [cfg.account]
    managed = _managed_accounts(ib)
    return managed or [None]


def _portfolio_items(ib: Any, account: str | None) -> list[Any]:
    try:
        return list(ib.portfolio(account)) if account else list(ib.portfolio())
    except TypeError:
        return list(ib.portfolio())


def _position_items(ib: Any, account: str | None) -> list[Any]:
    try:
        items = list(ib.positions(account)) if account else list(ib.positions())
    except TypeError:
        items = list(ib.positions())
    if account:
        items = [item for item in items if getattr(item, "account", account) == account]
    return items


def _cash_from_account_summary(ib: Any, account: str | None) -> float:
    try:
        summary = ib.accountSummary(account) if account else ib.accountSummary()
    except TypeError:
        summary = ib.accountSummary()
    except Exception:
        return 0.0

    preferred_tags = {"TotalCashValue", "CashBalance"}
    fallback = 0.0
    for item in summary:
        tag = str(getattr(item, "tag", "") or "")
        currency = str(getattr(item, "currency", "") or "").upper()
        value = _safe_float(getattr(item, "value", None))
        if value is None:
            continue
        if tag == "NetLiquidation" and currency in {"", "BASE", "USD"}:
            fallback = value
        if tag in preferred_tags and currency in {"", "BASE", "USD"}:
            return value
    return fallback


def _ensure_account_updates(ib: Any, account: str | None) -> None:
    try:
        ib.reqAccountUpdates(account or "")
    except Exception:
        pass


def _aggregate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = str(row.get("symbol", "") or "").strip()
        if not symbol:
            continue

        group = grouped.get(symbol)
        if group is None:
            group = {
                "symbol": symbol,
                "position": 0.0,
                "last": 0.0,
                "change_pct": None,
                "avg_price": 0.0,
                "cost_basis": 0.0,
                "market_value": 0.0,
                "unrealized_pl": 0.0,
                "unrealized_pl_pct": None,
                "pe": None,
                "eps_current": None,
            }
            grouped[symbol] = group

        position = _safe_float(row.get("position")) or 0.0
        cost_basis = _safe_float(row.get("cost_basis")) or 0.0
        market_value = _safe_float(row.get("market_value")) or 0.0
        unrealized_pl = _safe_float(row.get("unrealized_pl")) or 0.0
        last = _safe_float(row.get("last")) or 0.0

        group["position"] = float(group["position"]) + position
        group["cost_basis"] = float(group["cost_basis"]) + cost_basis
        group["market_value"] = float(group["market_value"]) + market_value
        group["unrealized_pl"] = float(group["unrealized_pl"]) + unrealized_pl
        if float(group["last"]) <= 0.0 and last > 0.0:
            group["last"] = last

    aggregated: list[dict[str, Any]] = []
    for group in grouped.values():
        position = float(group["position"])
        cost_basis = float(group["cost_basis"])
        market_value = float(group["market_value"])
        unrealized_pl = float(group["unrealized_pl"])

        avg_price = round(cost_basis / position, 6) if position else 0.0
        upl_pct = round((unrealized_pl / cost_basis) * 100, 2) if cost_basis else None

        aggregated.append(
            {
                **group,
                "position": round(position, 6),
                "avg_price": avg_price,
                "cost_basis": round(cost_basis, 2),
                "market_value": round(market_value, 2),
                "unrealized_pl": round(unrealized_pl, 2),
                "unrealized_pl_pct": upl_pct,
            }
        )
    aggregated.sort(key=lambda r: r["symbol"])
    return aggregated


def fetch_ibkr_portfolio(config: IBKRConnectionConfig | None = None, ib_factory: type | None = None) -> tuple[list[dict[str, Any]], float]:
    cfg = config or IBKRConnectionConfig.from_env()
    IB = ib_factory or _require_ib_class()
    ib = IB()
    try:
        ib.connect(
            cfg.host,
            cfg.port,
            clientId=cfg.client_id,
            timeout=cfg.timeout,
            readonly=cfg.readonly,
            account="",
        )
        accounts = _resolve_accounts(ib, cfg)
        rows: list[dict[str, Any]] = []
        cash = 0.0

        for account in accounts:
            _ensure_account_updates(ib, account)
            rows.extend(
                [
                    row
                    for row in (_row_from_portfolio_item(item) for item in _portfolio_items(ib, account))
                    if row is not None
                ]
            )
            cash += _cash_from_account_summary(ib, account)

        if not rows:
            for account in accounts:
                _ensure_account_updates(ib, account)
                rows.extend(
                    [
                        row
                        for row in (_row_from_position(item) for item in _position_items(ib, account))
                        if row is not None
                    ]
                )

        return _aggregate_rows(rows), round(cash, 2)
    finally:
        try:
            ib.disconnect()
        except Exception:
            pass
