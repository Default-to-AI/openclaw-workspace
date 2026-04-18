---
title: Kelly Criterion
type: entity
domain: finance
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy]]"
tags:
  - position-sizing
  - mathematics
  - framework
  - risk
---

# Kelly Criterion

A mathematical formula for determining the optimal size of a series of bets to maximize the long-run geometric growth rate of capital. Originally developed by John L. Kelly Jr. at Bell Labs in 1956 for information theory, it was subsequently adopted by gamblers and investors as a position-sizing framework.

## The formula

In its simplest form for a binary bet:

**f* = (bp - q) / b**

Where:
- **f*** = fraction of capital to bet
- **b** = odds received on the bet (net payout per dollar risked)
- **p** = probability of winning
- **q** = probability of losing (1 - p)

For investing, the inputs are estimated rather than known, which introduces a critical source of error.

## Half-Kelly in practice

The source framework explicitly advocates the **Half-Kelly strategy** — sizing positions at 50% of whatever the full Kelly formula recommends. The rationale is grounded in the asymmetry between upside sacrifice and downside protection:

- Full Kelly maximizes long-run growth but produces extreme portfolio volatility (drawdowns of 50%+ are expected and normal)
- Half Kelly captures approximately **75% of the maximum growth rate** while reducing volatility by roughly half
- The risk of total ruin drops from non-trivial (under full Kelly with estimation error) to near zero

This is not a conservative compromise — it is mathematically the superior strategy for anyone who (a) cannot estimate their edge with perfect precision (i.e., all investors), and (b) cannot psychologically endure the drawdowns that full Kelly produces ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

## Why estimation error matters

In gambling, the odds are known. In investing, both **p** (probability of the thesis being correct) and **b** (magnitude of the payoff) are estimates. Overestimating your edge by even a small amount under full Kelly can flip the formula from wealth-building to wealth-destroying. Half Kelly provides a buffer against this estimation error.

## Notable practitioners

The Kelly Criterion has been used by:
- **Ed Thorp** — mathematician who applied it to blackjack and then to hedge fund management (Princeton Newport Partners)
- **Warren Buffett** — has referenced the concept in the context of concentrating capital in highest-conviction ideas (see [[warren-buffett]])
- **Bill Gross** — applied Kelly-style thinking to bond portfolio construction

## See also

- [[position-sizing]]
- [[risk-management]]
- [[variant-perception]]
- [[warren-buffett]]
- [[hedge-fund-strategy-research]]
