# IBKR Live Dashboard Integration

Status: implementation artifact  
Owner: Axe Capital  
Broker: Interactive Brokers  
Library: `ib_async`  
Primary goal: present live broker portfolio/account data in the Axe Capital dashboard without enabling live order execution.

## Executive Summary

Axe Capital should use `ib_async` as a read-only adapter between Robert's Interactive Brokers account and the existing dashboard artifact pipeline.

Recommended production flow:

```text
IBKR TWS / IB Gateway
  -> ib_async read-only connection
  -> axe_portfolio live snapshot adapter
  -> normalized portfolio model
  -> step6-dashboard/public/portfolio.json
  -> dashboard Portfolio / Risk / Health panels
```

This keeps Interactive Brokers as the broker of record while preserving the current Axe Capital dashboard rule: the React dashboard renders JSON artifacts and does not compute portfolio state itself.

The first integration should be portfolio/account read-only only:
- positions
- market value
- average cost
- unrealized P&L
- cash
- account summary
- optional open orders for visibility

Live order placement is explicitly out of scope until paper-trading gates and approval workflow are implemented.

## Why `ib_async`

`ib_async` is the maintained successor-style async interface for Interactive Brokers. It provides a Python interface over TWS / IB Gateway and implements the IBKR protocol internally, so the separate `ibapi` package is not required.

Relevant upstream behavior:
- install package: `pip install ib_async`
- requires Python 3.10+
- requires running TWS or IB Gateway with API access enabled
- default ports: TWS `7497`, IB Gateway `4001`
- account APIs include `positions()`, `portfolio()`, `accountSummary()`, and `reqPnL()`
- market data can be real-time or delayed depending on Robert's IBKR subscriptions

Sources:
- `ib_async` docs: https://ib-api-reloaded.github.io/ib_async/index.html
- GitHub repo: https://github.com/ib-api-reloaded/ib_async

## Target Dashboard Contract

The dashboard should continue reading:

```text
projects/Axe-Capital/step6-dashboard/public/portfolio.json
```

The live broker integration should refresh that file with the same shape currently used by the dashboard:

```json
{
  "generated_at": "2026-04-15T18:00:00Z",
  "review_date": "2026-04-15",
  "positions": [
    {
      "symbol": "MSFT",
      "position": 2.0,
      "shares": 2.0,
      "last": 425.5,
      "last_price": 425.5,
      "avg_price": 400.0,
      "cost_basis": 800.0,
      "market_value": 851.0,
      "unrealized_pl": 51.0,
      "unrealized_pl_pct": 6.38,
      "sector_tag": "US Large Cap Tech",
      "weight_pct": 12.4,
      "stop_loss_level": 360.0,
      "distance_to_stop_pct": 15.39,
      "alert_status": "GREEN"
    }
  ],
  "summary": {
    "nav": 120079.0,
    "positions_value": 108222.0,
    "cash": 11857.0,
    "cash_pct": 9.9,
    "total_unrealized_pl": 1571.0,
    "total_unrealized_pl_pct": 1.47,
    "red_count": 0,
    "yellow_count": 1,
    "green_count": 11
  },
  "sector_weights": [],
  "hishtalmut": {}
}
```

The dashboard should not connect to IBKR directly. Browser-side broker connectivity would expose the wrong surface area and complicate credential/session control. The backend or refresh agent connects to IBKR locally, writes artifacts, and the dashboard renders those artifacts.

## Local IBKR Setup

Robert must run either TWS or IB Gateway locally.

Required IBKR settings:

```text
Configure -> API -> Settings
  [x] Enable ActiveX and Socket Clients
  Trusted IPs: 127.0.0.1
  Port:
    7497 for TWS paper/default local use
    4001 for IB Gateway
  [x] Download open orders on connection
```

Recommended:
- Start with paper account.
- Use a unique `clientId` for Axe Capital, e.g. `51`.
- Keep `readonly=True` for dashboard refreshes.
- Increase Gateway/TWS memory if bulk data refreshes become unstable.

## Environment Variables

The portfolio refresh process should be configured through env vars:

```bash
AXE_PORTFOLIO_SOURCE=ibkr
AXE_IBKR_HOST=127.0.0.1
AXE_IBKR_PORT=7497
AXE_IBKR_CLIENT_ID=51
AXE_IBKR_ACCOUNT=DU1234567
AXE_IBKR_READONLY=1
AXE_IBKR_TIMEOUT=10
```

Recommended modes:

```text
AXE_PORTFOLIO_SOURCE=csv   -> use existing CSV snapshot path only
AXE_PORTFOLIO_SOURCE=ibkr  -> require live IBKR connection; fail loudly if unavailable
AXE_PORTFOLIO_SOURCE=auto  -> try IBKR first, fall back to CSV
```

For production reliability, dashboard refresh should use `ibkr` mode when Robert expects live data. `auto` is useful during development but can hide outages by silently falling back to stale CSV.

## Implementation Design

The implementation belongs in Step 5, not the React dashboard.

Recommended files:

```text
step5-portfolio-tracking/
  axe_portfolio/
    ibkr.py        # read-only live IBKR adapter
    tracker.py     # source selection and artifact generation
    cli.py         # trace-wrapped refresh entrypoint
  tests/
    test_ibkr.py   # fake IB object, no real broker needed
```

Adapter responsibilities:

1. Load connection config from env.
2. Import `ib_async.IB` lazily so tests and CSV mode work without a broker install.
3. Connect read-only to TWS / Gateway.
4. Resolve account:
   - use `AXE_IBKR_ACCOUNT` if set
   - otherwise use first `managedAccounts()` result
5. Fetch portfolio rows via `ib.portfolio()`.
6. Fallback to `ib.positions()` if portfolio details are unavailable.
7. Fetch cash from `accountSummary()`, prioritizing `TotalCashValue` / `CashBalance`.
8. Disconnect in `finally`.
9. Return normalized rows compatible with the current `axe_portfolio.tracker` pipeline.

Normalized row contract:

```python
{
    "symbol": "MSFT",
    "position": 2.0,
    "last": 425.5,
    "change_pct": None,
    "avg_price": 400.0,
    "cost_basis": 800.0,
    "market_value": 851.0,
    "unrealized_pl": 51.0,
    "unrealized_pl_pct": 6.38,
    "pe": None,
    "eps_current": None,
}
```

The existing tracker then enriches this with:
- sector tags
- portfolio weights
- stop-loss levels
- distance-to-stop
- alert status
- dashboard summary

## Refresh Flow

Manual refresh:

```bash
cd projects/Axe-Capital/step5-portfolio-tracking
AXE_PORTFOLIO_SOURCE=ibkr python -m axe_portfolio.cli
```

Orchestrated refresh:

```bash
cd projects/Axe-Capital/step7-automation
AXE_PORTFOLIO_SOURCE=ibkr python -m axe_orchestrator.cli run portfolio
```

Dashboard API refresh target:

```text
POST /refresh/portfolio
  -> step7 runner invokes axe_portfolio.cli
  -> axe_portfolio writes portfolio.json
  -> health.json updates freshness
  -> dashboard re-reads artifact
```

## Live Data Semantics

Expected IBKR data fields:

```text
PortfolioItem.contract.symbol       -> symbol
PortfolioItem.position              -> shares / quantity
PortfolioItem.marketPrice           -> last
PortfolioItem.averageCost           -> avg_price
PortfolioItem.marketValue           -> market_value
PortfolioItem.unrealizedPNL         -> unrealized_pl
AccountSummary.TotalCashValue       -> cash
```

Important caveats:
- `marketPrice` depends on market data permissions and delayed/real-time setting.
- Portfolio data can be empty immediately after connection; refresh may need a short wait in later versions.
- Some instruments may have `localSymbol` instead of clean `symbol`; adapter should prefer `contract.symbol`, fallback to `localSymbol`.
- Cash can appear in multiple currencies. Initial implementation should prioritize USD/base only, then add FX conversion later if needed.

## Safety Rules

Hard boundaries:
- Do not place orders from the dashboard integration.
- Do not expose IBKR credentials in frontend code.
- Do not store account passwords in repo files.
- Do not write raw broker exports into the Obsidian vault from agents.
- Do not enable live execution until Robert explicitly approves it.

Recommended adapter safeguards:
- connect with `readonly=True`
- no imports of order classes in the read-only adapter
- no `placeOrder()` usage in Step 5
- separate future execution module from portfolio snapshot module
- trace every refresh run
- fail loudly in `ibkr` mode if broker is unavailable

## Testing Plan

Unit tests:
- fake `IB` object returns portfolio rows and account summary
- verify row normalization
- verify cash extraction
- verify disconnect is called
- verify cash/security instruments are skipped

Integration smoke test with TWS / Gateway running:

```bash
cd projects/Axe-Capital/step5-portfolio-tracking
AXE_PORTFOLIO_SOURCE=ibkr \
AXE_IBKR_HOST=127.0.0.1 \
AXE_IBKR_PORT=7497 \
AXE_IBKR_CLIENT_ID=51 \
python -m axe_portfolio.cli
```

Expected result:
- command exits `0`
- `dashboard/data/portfolio_latest.normalized.csv` refreshes
- `step6-dashboard/public/portfolio.json` refreshes
- `step6-dashboard/public/traces/index.json` records a successful `axe_portfolio` run
- dashboard Portfolio panel shows current broker positions

## Rollout Checklist

- [ ] Install dependency in Axe Capital venv: `pip install -e step5-portfolio-tracking`
- [ ] Confirm `ib_async` is installed in the venv
- [ ] Start TWS or IB Gateway
- [ ] Enable API socket clients
- [ ] Confirm correct port: `7497` TWS or `4001` Gateway
- [ ] Run Step 5 with `AXE_PORTFOLIO_SOURCE=ibkr`
- [ ] Inspect generated `portfolio.json`
- [ ] Open dashboard and verify Portfolio panel renders live values
- [ ] Run `/refresh/portfolio` through the local API
- [ ] Verify health panel freshness changes after refresh
- [ ] Keep `AXE_PORTFOLIO_SOURCE=csv` available as fallback during early rollout

## Future Extensions

Phase 2:
- live open orders visibility
- daily realized P&L
- intraday unrealized P&L stream
- stale broker-session alert
- multi-currency cash breakdown

Phase 3:
- paper-trading order proposal adapter
- explicit approval queue before execution
- order preview in dashboard
- audit trail for submitted paper orders

Phase 4:
- live execution only after paper track record and explicit approval downgrade.

