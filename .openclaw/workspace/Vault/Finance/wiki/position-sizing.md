---
title: Position Sizing
type: concept
domain: finance
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy]]"
tags:
  - portfolio-construction
  - risk
  - concentration
  - diversification
---

# Position Sizing

Position sizing determines how much capital to allocate to each investment idea. It is arguably the single most important factor in portfolio management — a brilliant stock pick with reckless sizing destroys capital, while a mediocre pick with disciplined sizing preserves it.

## Asymmetric risk-reward as a prerequisite

Every position must be structured so that the potential upside heavily dwarfs the downside. The target is risking a small, fixed amount to potentially make massive multiples of the initial investment. If a setup does not offer asymmetric payoff characteristics, it does not deserve capital regardless of conviction level ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

**Practical framing**: Before entry, define the downside (invalidation point from [[risk-management]]) and the upside (target price from [[variant-perception|variant perception]]). If the ratio is not at least 3:1 reward-to-risk, pass.

## The Half-Kelly strategy

The [[kelly-criterion|Kelly Criterion]] provides a mathematically optimal bet size given your edge (probability of winning) and the payoff ratio. However, full Kelly sizing produces extreme volatility that is psychologically and practically unmanageable.

The **Half-Kelly** approach sizes each position at 50% of what the full Kelly formula dictates. This trade-off is highly favorable:

| Metric | Full Kelly | Half Kelly |
|--------|-----------|------------|
| Long-run growth rate | Maximum | ~75% of maximum |
| Portfolio volatility | Extreme | Dramatically reduced |
| Risk of ruin | Non-trivial | Near zero |
| Psychological sustainability | Very low | High |

You sacrifice roughly 25% of the theoretical optimal growth rate but eliminate the catastrophic tail risk and emotional blowups that full Kelly creates ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

## The 20-punch card

A mental model attributed to [[warren-buffett|Warren Buffett]]: imagine you receive a card with only twenty slots, and each investment you make punches one slot. When the card is full, you can never invest again.

This forces:
- **Extreme selectivity** — most ideas get discarded not because they are bad, but because they are not exceptional
- **Deep conviction** — every allocation represents a bet you would be comfortable holding through significant adversity
- **Patience** — waiting for a truly outstanding setup rather than deploying capital into "good enough" ideas

In practice, no one literally limits themselves to twenty investments. The model's value is as a decision filter: "Is this idea good enough to use one of my twenty punches?" If the answer is not an emphatic yes, move on ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

## Strategic diversification

Diversification is not owning many stocks — it is owning *uncorrelated* exposures. Holding 30 tech stocks is not diversified. The source framework, drawing on [[peter-lynch|Peter Lynch's]] stock categorization, advocates diversifying across business life cycles:

| Category | Characteristics | Role in portfolio |
|----------|----------------|-------------------|
| Slow growers | Mature, stable, high dividend | Ballast, income |
| Stalwarts | Large caps, steady 10-12% growth | Core holdings, downside protection |
| Fast growers | Small/mid, 20-50%+ growth | Primary return driver |
| Cyclicals | Earnings tied to economic cycle | Tactical, timing-dependent |
| Turnarounds | Distressed, potential recovery | High asymmetry, event-driven |
| Asset plays | Hidden value on balance sheet | Free optionality |

A portfolio blending several categories achieves genuine diversification because the drivers of each category's returns are different ([[(To Ingest) YouTube Research - Stock Picking Hedge Fund Strategy|source]]).

## See also

- [[kelly-criterion]]
- [[risk-management]]
- [[variant-perception]]
- [[selling-discipline]]
- [[warren-buffett]]
- [[peter-lynch]]
- [[hedge-fund-strategy-research]]
