---
type: spec
project: axe-capital
status: draft
created: 2026-04-11
tags: [axe-capital, agents, org, contracts]
---

# Axe Capital — Hedge-Fund Agent Org (Draft)

## North star
Decisions are made like a disciplined hedge fund:
- independent analysis streams
- explicit risk wrapper
- written investment memos
- a single final decision-maker (CEO)
- you execute manually

## Roles

### CEO (Final decision-maker)
**Inputs:** all reports + risk constraints + portfolio constraints
**Output:** 0–3 actions with rationale + sizing + invalidation + profit-taking targets
**Cannot:** fetch raw data (delegates)

### COO/CFO (Operations + capital allocator)
**COO:** ensures process runs, assigns work, checks completeness
**CFO:** checks exposures, liquidity, constraints, portfolio-level sizing

### Portfolio Manager (PM)
Owns portfolio construction: concentration, diversification, factor tilts.

### Risk Manager
Enforces risk limits, max drawdown, scenario checks, correlation, position limits.
Can veto.

### Fundamental Analyst
Business quality, earnings, balance sheet, valuation ranges, thesis.

### Technical Analyst
Regime/market structure, entry/exit levels, trend confirmation, invalidation levels.

### Macro Strategist
Rates, USD, liquidity, sector rotation context, "what regime are we in".

### Compliance/Audit (internal)
Ensures every decision has:
- sources
- assumptions
- constraints checks
- an audit trail

## Reporting cadence
- Weekly: full portfolio review + 1–3 proposals
- Daily: risk monitor + thesis-break alerts

## Output contracts (files)
Each agent writes into its own folder:
- `.../Reports/<agent-name>/YYYY-MM-DD.md`
CEO output goes to:
- `02_Plans/approval-queue.md` + `04_DecisionLog/YYYY-MM-DD__TICKER__action.md`

## Approval gates
- Paper-only until explicitly changed.
- CEO can propose; you approve/execute.
