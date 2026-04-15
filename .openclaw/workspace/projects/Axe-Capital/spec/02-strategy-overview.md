---
type: spec
project: axe-capital
status: draft
created: 2026-04-11
tags: [axe-capital, strategy]
---

# Strategy Overview (Draft)

This is intentionally conservative: we optimize for *not blowing up*, and for *repeatable process*.

## Core loop
1) **Universe & watchlist** (your current holdings + a screened universe)
2) **Research** (filings, earnings, news, factor stats)
3) **Thesis formation** (why now, what must be true)
4) **Risk wrapper** (sizing, exposure limits, correlation, scenario checks)
5) **Order proposal** (entries, exits, contingencies)
6) **Approval** (you)
7) **Execution** (IBKR)
8) **Post-trade** (fill quality, drift, thesis monitoring)

## Edges we can actually build
- **Process edge**: consistent screening + checklists + decision logging.
- **Time arbitrage**: multi-month thesis horizon, avoid noise.
- **Risk discipline**: hard caps and fast invalidation.

## What we will *not* do in early phases
- High leverage, options, complex derivatives.
- Fully autonomous live execution without a long paper track record.
