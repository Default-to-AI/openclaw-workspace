---
type: dashboard
project: AxeCapital
created: 2026-04-11
mode: phase1-manual-csv
---

# Axe Dashboard

## 1) Portfolio snapshot (normalized)
Sources:
- Raw: `00_Dashboard/data/raw/portfolio-current-10-April.csv`
- Normalized (stable): `00_Dashboard/data/portfolio_latest.normalized.csv`

### Quick KPIs (computed from latest normalized snapshot)
- Total market value (ex-cash): **$108,222**
- Cash: **$11,700**
- NAV estimate (market value + cash): **$119,922**
- Total unrealized P&L (ex-cash): **$1,568**
- Unrealized P&L % (ex-cash, vs cost basis): **1.47%**

### Portfolio Table (Dataview)

```dataview
TABLE
  symbol as Symbol,
  position as Pos,
  last as Last,
  change_pct + "%" as "Chg%",
  avg_price as Avg,
  cost_basis as Cost,
  market_value as MV,
  unrealized_pl as "UPL$",
  unrealized_pl_pct + "%" as "UPL%"
FROM csv("50_AISphere/Projects/AxeCapital/00_Dashboard/data/portfolio_latest.normalized.csv")
WHERE symbol != "Total"
SORT market_value desc
```

Columns in CSV: `symbol, position, last, change_pct, avg_price, cost_basis, market_value, unrealized_pl, unrealized_pl_pct, pe, eps_current`

View note:
- `00_Dashboard/views/portfolio_view.md`

## 2) P&L (Phase 1, normalized inputs)
Normalized inputs (stable filenames):
- Portfolio snapshot (unrealized by line): `00_Dashboard/data/portfolio_latest.normalized.csv`
- Activity statement KV: `00_Dashboard/data/activity_kv.latest.csv`
- Realized summary KV: `00_Dashboard/data/realized_kv.latest.csv`
- MTM summary KV: `00_Dashboard/data/mtm_kv.latest.csv`

Status: **Inputs normalized. Rendering next.**

What will show here (phase 1):
- Unrealized P&L (from portfolio snapshot)
- Realized P&L (best-effort from realized summary)
- Fees, dividends/interest (best-effort from activity)
- Cash + rough NAV estimate (portfolio cash + market value)

## 3) Watchlists + Targets
Status: **Not built yet**.
Will contain:
- Watchlist (tickers, thesis in 1 line, trigger levels)
- “Approaching target” list (within X% of trigger)

## 4) News (per ticker)
Status: **Not built yet**.
Phase 1 will be: manual links + a daily pull via web_fetch into a news note.

## 5) Suggestions queue (paper-first)
Links:
- Approval queue: `02_Plans/approval-queue.md`
- IC Packet template: `02_Plans/IC_Packet_Template.md`

## 6) Agents: what they’re thinking + logs
Status: **Not built yet**.
This will link to:
- `05_Logs/Agents/<agent>/YYYY-MM-DD.md`
- each log includes: focus, open questions, next output, reasoning summary
