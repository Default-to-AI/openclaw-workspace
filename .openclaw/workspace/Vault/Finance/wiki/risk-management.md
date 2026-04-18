---
title: Risk Management
type: concept
domain: finance
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy]]"
tags:
  - risk
  - drawdown
  - stop-loss
  - capital-preservation
---

# Risk Management

Risk management in stock picking is the discipline of defining, measuring, and controlling the conditions under which capital is lost. The source framework defines risk as **permanent loss of capital** — not price volatility, not tracking error, not drawdowns per se — but the irrecoverable destruction of purchasing power.

## Pre-defined invalidation points

Before deploying a single dollar, establish the exact price level or fundamental data point that proves your hypothesis wrong. This is non-negotiable.

An invalidation point is not an arbitrary percentage — it is derived from the thesis itself:
- If your thesis depends on a revenue inflection, the invalidation is the earnings report that shows no inflection
- If your thesis depends on a balance sheet restructuring, the invalidation is the restructuring failing
- If your thesis depends on a price floor set by asset value, the invalidation is the stock trading below that floor

Writing the invalidation down before entry removes the temptation to move the goalposts after the fact ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

## The 3% rule

A mechanical capital-preservation protocol:

1. If a position (or allocated capital tranche) loses **3%**, cut the size in half immediately
2. If it declines further from the reduced position, liquidate entirely

The purpose is to remove emotion from loss-taking. The 3% threshold is deliberately tight — it accepts frequent small losses in exchange for preventing any single position from inflicting meaningful portfolio damage ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

## Mental stops over hard stop-losses

The framework advocates replacing rigid automatic stop-loss orders with mental stops. The distinction matters:

| | Hard stop-loss | Mental stop |
|---|---|---|
| Execution | Automatic, market order at trigger | Manual, deliberate |
| Risk of whipsaw | High (market makers hunt stops) | Low |
| Psychological effect | Clean but abrupt | Managed through incremental exit |
| Best for | Day trading, highly liquid positions | Multi-week to multi-year holdings |

When an invalidation point is hit, the recommended protocol is **incremental liquidation** — selling the position in chunks rather than all at once. This serves a psychological function: it eases the pain of admitting defeat and prevents the ego-driven reflex to "hold and hope" ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

## Time as a stop-loss

Capital has an opportunity cost. A stock that is not declining but is not performing within your anticipated timeframe is consuming two scarce resources:

1. **Capital** — money sitting in a dead position cannot be deployed into a higher-probability setup
2. **Mental bandwidth** — every open position occupies cognitive real estate; stagnant positions drain attention without generating returns

If a position has not moved toward your thesis within the defined timeframe, cut it and redeploy. This is not a failure of analysis — it is an acknowledgment that the catalyst's timing was wrong, which is functionally equivalent to the catalyst not existing ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

## Integration with the weekly workflow

In the [[hedge-fund-strategy-research#Weekly workflow|weekly workflow]], risk management is a daily (Mon-Fri) activity:
- Check whether any holdings have hit their pre-defined invalidation points
- If triggered, initiate the loss-harvesting protocol immediately, without second-guessing
- No discretionary overrides — the invalidation was set when thinking was clear; the current moment is contaminated by loss aversion

## See also

- [[position-sizing]]
- [[selling-discipline]]
- [[behavioral-traps]]
- [[kelly-criterion]]
- [[hedge-fund-strategy-research]]
