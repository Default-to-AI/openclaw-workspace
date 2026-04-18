# Axe Capital – IBKR portfolio sync (session summary)
Date: 2026-04-16

## What you reported
- Pipeline runs, but avg_price was being copied into last (or equivalently cost_basis == market_value), so every position showed 0 unrealized P/L and portfolio return 0%.
- Good news: it successfully pulled both portfolios’ positions (main + small QQQ-only account).

## What we verified
- `step7-automation/check_artifacts.sh` showed outputs were being produced (portfolio.json, alpha-latest.json, news-latest.json, health.json, traces/index.json).
- The prototype server issues were port collisions plus stale pid files.

## Fixes applied (code changes)
### 0) Dashboard refresh vs UI update
Files:
- `step6-dashboard/vite.config.js`
- `step6-dashboard/src/lib/api.js`

Notes:
- The dashboard uses a Vite dev proxy for `/api/*` which forwards to `localhost:8000` and strips the `/api` prefix.
- Refresh is triggered via `POST /api/refresh/<target>` (proxy forwards to backend `POST /refresh/<target>`).
- To prevent “refresh ran but UI still shows old data”, we patched `src/lib/api.js` to fetch with `cache: 'no-store'` and add a cache-busting query param.

### 1) Prototype launcher reliability
File: `projects/Axe-Capital/step7-automation/start_prototype.sh`
- Cleans stale PID files (`logs/api.pid`, `logs/dashboard.pid`).
- Auto-picks free ports starting at 8000 (API) and 5173 (dashboard).
- Prints the final URLs.

### 2) Root cause of zero P/L
File: `projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/ibkr.py`
- Primary path (`portfolio()`) is fine.
- Fallback path when `portfolio()` returns no rows used `positions()` which does not include live market prices.
- Old behavior set `last = avg_price`, which forces 0 P/L.

Changes:
- `_row_from_position` now sets `last = 0.0` (instead of lying) and tags `ibkr_source="positions"`.
- In `fetch_ibkr_portfolio()`, when falling back to positions, we:
  - try to request delayed quotes (`reqMarketDataType(3)`)
  - force contracts to `exchange="SMART"`
  - try `reqTickers()` to fill last prices and recompute market_value + P/L
  - if IBKR denies quotes (or `reqTickers` fails), we fall back to **yfinance** to fill `last` and compute P/L.

### 3) CSV export support (workaround + safety net)
File: `projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/tracker.py`
- Your export `dashboard/data/csv-ibkr-positions.csv` header includes: Financial Instrument, Last, Position, Avg Price, Unrealized P&L, Market Value.
- It does not include Cost Basis.

We relaxed RAW_HEADER and added derivations:
- `cost_basis = position * avg_price` if missing
- `market_value = position * last` if missing
- derive `unrealized_pl` and `unrealized_pl_pct` if missing

So `AXE_PORTFOLIO_SOURCE=csv` works cleanly with your export.

## Where we stopped (current blocker)
### 1) IBKR quotes via API denied
When running IBKR mode:
```bash
AXE_PORTFOLIO_SOURCE=ibkr ... python -m axe_orchestrator.cli run portfolio
```
IBKR returned market data permission errors:
- 10168: market data not subscribed, delayed market data not enabled
- 10089: market data requires additional subscription for API

### 2) Fix applied (no more CSV required)
We patched `axe_portfolio/ibkr.py` so that when IBKR denies quotes, we **fall back to yfinance** to fill `last` (positions and avg_cost still come from IBKR).
This makes P/L compute correctly without manual exports.

## Next-step options
A) Keep yfinance fallback (recommended for now): reliable, zero IB subscription headaches.
B) Get IBKR API quotes working: enable delayed data or add the required market data entitlements for API, then remove/disable fallback if desired.

## Useful commands
Check active python:
```bash
which python
python -c "import sys; print(sys.executable)"
```

Run portfolio (IBKR):
```bash
AXE_PORTFOLIO_SOURCE=ibkr /home/tiger/.openclaw/workspace/projects/Axe-Capital/.venv/bin/python -m axe_orchestrator.cli run portfolio
```

Run portfolio (CSV export):
```bash
AXE_PORTFOLIO_SOURCE=csv /home/tiger/.openclaw/workspace/projects/Axe-Capital/.venv/bin/python -m axe_orchestrator.cli run portfolio
```

## External reference you shared
IBKR Campus: https://www.interactivebrokers.com/campus/trading-lessons/python-account-portfolio/
Mentions the API subscribe/publish model and functions like `reqAccountUpdates` and `reqPositions`.
