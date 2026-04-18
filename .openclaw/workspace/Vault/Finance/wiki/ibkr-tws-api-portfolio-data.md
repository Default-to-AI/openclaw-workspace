---
title: TWS API — Portfolio and Account Data
type: source-summary
domain: finance
created: 18-04-2026
updated: 18-04-2026
sources:
  - "[[Finance/raw/16-04-2026-ibkr-tws-api-portfolio-data]]"
tags:
  - ibkr
  - tws-api
  - python
  - portfolio-data
  - account-data
---

# TWS API — Portfolio and Account Data

Official IBKR tutorial on using the TWS Python API to access real-time portfolio positions and account data. Core to any programmatic IBKR integration.

## The Subscribe-and-Publish Model

All position/account functions follow the same pattern:
1. Call the subscribe function
2. TWS sends back a full initial snapshot
3. EWrapper callbacks stream real-time updates as changes occur
4. Call the cancel/stop function to unsubscribe

`accountDownloadEnd` fires once after the initial full batch; subsequent updates are incremental (only changed values).

## Five Functions — When to Use Which

### Position Data

| Function | Use Case |
|---|---|
| `ReqAccountUpdates(True, account)` | Single account — returns both positions AND account data in one call |
| `ReqPositions()` | Up to 50 sub-accounts simultaneously |
| `ReqPositionsMulti()` | >50 sub-accounts, or a specific model portfolio |

### Account Data

| Function | Use Case |
|---|---|
| `ReqAccountUpdates(True, account)` | Single account (returns both positions and account data) |
| `reqAccountSummary()` | Multiple accounts at once |
| `reqAccountSummaryMulti()` | Single sub-account when >50 sub-accounts exist |

For a standard single-account IBKR setup (Robert's case), `ReqAccountUpdates` is the go-to: one call covers everything.

## Key Callbacks (ReqAccountUpdates)

- `updateAccountValue(key, val, currency, accountName)` — one callback per account key (cash balance, margin, net liquidation value, etc.), alphabetical order
- `updatePortfolio(contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName)` — one callback per position
- `updateAccountTime(timeStamp)` — timestamp of data
- `accountDownloadEnd(accountName)` — signals end of initial full batch

## Virtual Cash vs. Real Cash

A common gotcha:

- **Real cash balances** → returned via `updateAccountValue`, listed as a single currency (e.g., `USD: 50000`)
- **Virtual cash positions** → returned via `updatePortfolio`, represented as forex pairs (e.g., `EUR.USD`) — these are forex trade bookmarks, NOT actual cash

## Historical Positions — Not Available

The API only provides current positions. Historical position data is **not available** via the API by design.

For historical data, use:
- **Flex Queries** — configurable reports in Account Management
- **Statements** — periodic account statements
- **Flexweb Service** — programmatic access to flex queries

## Connection

TWS must be running locally. Connect via socket:
- `app.connect("127.0.0.1", 7497, 0)` — port 7497 is TWS paper trading; live trading uses 7496

## See also

- [[interactive-brokers]]
- [[algorithmic-trading-with-llms]]
