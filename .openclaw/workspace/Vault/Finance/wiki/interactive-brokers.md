---
title: Interactive Brokers (IBKR)
type: entity
domain: finance
created: 18-04-2026
updated: 18-04-2026
sources:
  - "[[Finance/raw/16-04-2026-ibkr-tws-api-portfolio-data]]"
tags:
  - ibkr
  - brokerage
  - tws-api
  - us-equities
---

# Interactive Brokers (IBKR)

Robert's primary brokerage for US equity investing (self-directed). IBKR is known for low commissions, direct market access, and a powerful (if complex) API ecosystem.

## Trader Workstation (TWS)

The desktop trading application. Also serves as the local socket server for API connections — must be running for programmatic access to work.

- **Paper trading port:** 7497
- **Live trading port:** 7496

## TWS API

Python library (`ibapi`) for programmatic access to account data, positions, market data, and order execution. Uses a subscribe-and-publish model: request once, receive real-time streaming updates via EWrapper callbacks.

Key function groups:
- **Position data:** `ReqAccountUpdates`, `ReqPositions`, `ReqPositionsMulti`
- **Account data:** `ReqAccountUpdates`, `reqAccountSummary`, `reqAccountSummaryMulti`
- **Order execution:** (separate lesson series)

Full reference: [TWS API User Guide](https://interactivebrokers.github.io/tws-api/)

## Important Limitations

- **No historical position data via API.** Current positions only. For historical data, use Flex Queries or Account Management statements (Flexweb service for programmatic access).
- **Virtual cash positions** (forex pairs like EUR.USD) are distinct from real cash balances (returned as single currency via account data, not position data).

## Robert's Usage

Primary vehicle for self-directed US equity investing. Programmatic access via TWS API is relevant for portfolio dashboards, automated tracking, and any LLM-trading integrations (e.g., [[algorithmic-trading-with-llms]]).

## See also

- [[ibkr-tws-api-portfolio-data]]
- [[algorithmic-trading-with-llms]]
