# Axe Capital — Hedge Fund Target Operating Model (TOM)

## 1) Purpose and design principles
- **Core purpose**: consistent compounding with controlled drawdowns via repeatable process.
- **Separation of duties**: Portfolio decision authority is distinct from governance and controls.
- **One source of truth**: positions, exposures, PnL, risk, and decisions are reconciled daily.
- **Pre-mortem culture**: the default assumption is that any trade can be wrong.

## 2) Functions and what “good” looks like
### Front Office
- **PM / CIO**: defines strategy, risk budgets, final trade decisions, hires/trains analysts.
- **Analysts**: idea generation, research, modeling, variant perception, catalysts, downside.
- **Trader / Execution**: best execution, routing, liquidity planning, slippage control.

### Risk & Controls (independent where possible)
- **Risk Manager**: independent risk view, factor/cluster exposure, stress tests, limits.
- **Compliance**: MNPI policy, restricted lists, personal trading, marketing rules, surveillance.

### Operations & Finance
- **Ops / Middle Office**: trade capture, confirmations, reconciliations, corporate actions.
- **Fund Controller**: NAV support, expense allocations, performance fees, audit readiness.
- **Treasury / Financing**: primes, margin, financing terms, cash forecasting.

### Technology & Data
- **Data/Eng**: research data pipelines, position/risk dashboards, logging/knowledge system.

### Investor Relations
- **IR**: reporting cadence, narrative, DDQs, transparency pack, inbound/outbound comms.

## 3) Decision system
### Decision types
- **Strategic**: mandate, instruments, leverage, liquidity profile, risk limits.
- **Portfolio**: new position, add/reduce, hedge changes, exit.
- **Operational**: brokers, vendors, tooling, pricing sources.

### Investment Committee (IC) as governance
For an institutional-style IC, the best practice framing is **governance, not investing**: ensure investing is executed in compliance with the agreed investment policy, risk tolerance, and process. (Partners Capital, 2026, summarizing Charles D. Ellis’ view.)

## 4) Artifacts
- **Investment Policy / Risk Charter** (risk appetite, constraints, limits)
- **IC Charter** (roles, quorum, voting, conflicts)
- **IC Packet** (pre-read) and **Decision Log** (post)
- **Daily risk report** + **weekly exposures** + **monthly performance attribution**
- **Playbooks**: earnings, macro events, drawdown protocol, crisis liquidity

## 5) Key controls
- Limits: gross/net, single-name, sector, factor, liquidity, stop/kill-switch.
- Independent reconciliations (positions/cash) and valuation sources.
- Pre-trade compliance checks.
- Post-trade review: thesis tracking, slippage, error taxonomy.

## 6) Cadence summary (see dedicated cadence doc)
- Daily: risk/exposure, PnL, reconciliation, watchlist and catalyst map.
- Weekly: portfolio review + risk deep dive + research pipeline review.
- Monthly: performance attribution, limits review, ops/compliance review.
- Quarterly: strategy review, scenario planning, stakeholder reporting.
