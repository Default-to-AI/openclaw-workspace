from __future__ import annotations

import os
import threading
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
    for module in ("ib_insync", "ib_async"):
        try:
            import importlib
            mod = importlib.import_module(module)
            return mod.IB
        except ImportError:
            continue
    raise RuntimeError(
        "Neither ib_insync nor ib_async is installed. "
        "Run: pip install ib_insync   (or pip install ib_async)"
    )


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
        # NOTE: positions() does not include live market prices.
        # Setting last=avg_price makes P/L appear as 0 by construction.
        # tracker.py will repair last/market_value/upl via yfinance when this fallback is used.
        "last": 0.0,
        "change_pct": None,
        "avg_price": avg_price,
        "cost_basis": round(position * avg_price, 2),
        "market_value": round(position * avg_price, 2),
        "unrealized_pl": 0.0,
        "unrealized_pl_pct": 0.0,
        "pe": None,
        "eps_current": None,
        "ibkr_source": "positions",
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


def _contracts_from_positions(items: list[Any]) -> list[Any]:
    contracts: list[Any] = []
    seen: set[tuple[str, str]] = set()
    for it in items:
        c = getattr(it, "contract", None)
        if c is None:
            continue
        sym = str(getattr(c, "symbol", "") or "").strip()
        lsym = str(getattr(c, "localSymbol", "") or "").strip()
        key = (sym, lsym)
        if key in seen:
            continue
        seen.add(key)
        contracts.append(c)
    return contracts


def _last_by_symbol_from_tick_data(tickers: list[Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for t in tickers:
        c = getattr(t, "contract", None)
        sym = _symbol_from_contract(c) if c is not None else ""
        if not sym:
            continue
        last = _safe_float(getattr(t, "last", None))
        if last is None or last <= 0:
            last = _safe_float(getattr(t, "close", None))
        if last is None or last <= 0:
            last = _safe_float(getattr(t, "marketPrice", None))
        if last is None or last <= 0:
            continue
        out[sym] = float(last)
    return out


def _fill_last_prices_from_ibkr(_ib: Any, rows: list[dict[str, Any]], position_items: list[Any]) -> list[dict[str, Any]]:
    """Fill last prices for rows produced via positions() fallback using yfinance.

    We skip ib.reqTickers() entirely: it requires snapshot market data permissions
    that most IBKR accounts don't have, and calling it from a non-asyncio thread
    (needed for timeout safety) conflicts with ib_async's event loop ownership.
    yfinance provides reliable delayed prices for all the symbols we hold.
    """
    if not rows:
        return rows

    last_by_symbol: dict[str, float] = {}
    missing_symbols = sorted({str(r.get("symbol") or "").strip() for r in rows if (r.get("last") or 0.0) <= 0.0})
    missing_symbols = [s for s in missing_symbols if s]
    if missing_symbols:
        try:
            import yfinance as yf  # type: ignore

            data = yf.download(
                tickers=" ".join(missing_symbols),
                period="5d",
                interval="1d",
                group_by="ticker",
                auto_adjust=False,
                progress=False,
                threads=True,
            )
            if len(missing_symbols) == 1:
                close = data.get("Close")
                if close is not None:
                    close = close.dropna()
                    if not close.empty:
                        last_by_symbol[missing_symbols[0]] = float(close.iloc[-1])
            else:
                for sym in missing_symbols:
                    try:
                        close = data[sym]["Close"].dropna()
                        if not close.empty:
                            last_by_symbol[sym] = float(close.iloc[-1])
                    except Exception:
                        continue
        except Exception:
            pass

    if not last_by_symbol:
        return rows

    filled: list[dict[str, Any]] = []
    for r in rows:
        sym = str(r.get("symbol") or "").strip()
        if not sym:
            filled.append(r)
            continue
        last = float(last_by_symbol.get(sym) or 0.0)
        if last > 0:
            position = float(_safe_float(r.get("position")) or 0.0)
            avg_price = float(_safe_float(r.get("avg_price")) or 0.0)
            cost_basis = round(position * avg_price, 2)
            market_value = round(position * last, 2)
            unrealized_pl = round(market_value - cost_basis, 2)
            upl_pct = round((unrealized_pl / cost_basis) * 100, 2) if cost_basis else None
            filled.append(
                {
                    **r,
                    "last": last,
                    "cost_basis": cost_basis,
                    "market_value": market_value,
                    "unrealized_pl": unrealized_pl,
                    "unrealized_pl_pct": upl_pct,
                }
            )
        else:
            filled.append(r)
    return filled


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


def _ensure_account_updates(ib: Any, account: str | None, timeout: float = 8.0) -> None:
    # ib_async.reqAccountUpdates() is blocking with RequestTimeout=0 (no timeout).
    # If TWS never sends accountDownloadEnd, it hangs forever.
    # We use the underlying async method + util.run(timeout=N) to cap the wait.
    # ib_insync has a different signature: reqAccountUpdates(subscribe: bool, acctCode: str).
    import inspect
    try:
        from ib_async import util as _ib_util
        # ib_async path: use async method with timeout
        async_method = getattr(ib, "reqAccountUpdatesAsync", None)
        if async_method is not None:
            try:
                _ib_util.run(async_method(account or ""), timeout=timeout)
            except Exception:
                pass
            return
    except ImportError:
        pass

    # ib_insync fallback: reqAccountUpdates(subscribe, acctCode)
    try:
        sig = inspect.signature(ib.reqAccountUpdates)
        params = list(sig.parameters)
        if len(params) >= 2 and params[0] == "subscribe":
            ib.reqAccountUpdates(True, account or "")
        else:
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


def _silent_disconnect(ib: Any) -> None:
    try:
        t = threading.Thread(target=ib.disconnect, daemon=True)
        t.start()
        t.join(timeout=3.0)
    except Exception:
        pass


def fetch_ibkr_portfolio(config: IBKRConnectionConfig | None = None, ib_factory: type | None = None) -> tuple[list[dict[str, Any]], float]:
    """Connect to TWS and return (rows, cash).

    TWS keeps a clientId locked for ~60s after a process is killed (SIGKILL).
    We try cfg.client_id, then cfg.client_id+1 … +4 so rapid restarts during
    development never block on a stale slot. ConnectionRefusedError (TWS not
    running) aborts immediately; TimeoutError on each attempt means the slot
    is likely in use, so we try the next one.
    Each IB() instance holds asyncio state, so we create a fresh one per attempt.
    """
    cfg = config or IBKRConnectionConfig.from_env()
    IB = ib_factory or _require_ib_class()

    last_exc: Exception = RuntimeError("no connection attempts made")
    ib: Any = None
    for offset in range(5):
        client_id = cfg.client_id + offset
        # Use a shorter timeout for fallback slots so stale IB instances die fast.
        connect_timeout = cfg.timeout if offset == 0 else min(cfg.timeout, 4.0)
        candidate = IB()
        try:
            candidate.connect(
                cfg.host,
                cfg.port,
                clientId=client_id,
                timeout=connect_timeout,
                readonly=cfg.readonly,
                account="",
            )
            ib = candidate
            break
        except ConnectionRefusedError as exc:
            # TWS is not running at all — no point retrying.
            last_exc = exc
            _silent_disconnect(candidate)
            raise
        except Exception as exc:
            last_exc = exc
            _silent_disconnect(candidate)

    if ib is None:
        raise last_exc

    try:
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
            position_items: list[Any] = []
            for account in accounts:
                _ensure_account_updates(ib, account)
                position_items.extend(_position_items(ib, account))
            rows = [row for row in (_row_from_position(item) for item in position_items) if row is not None]
            rows = _fill_last_prices_from_ibkr(ib, rows, position_items)

        return _aggregate_rows(rows), round(cash, 2)
    finally:
        _silent_disconnect(ib)
