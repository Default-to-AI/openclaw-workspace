---
type: research
project: axe-capital
status: draft
created: 2026-04-11
tags: [axe-capital, research, hedge-fund, org]
---

# Research rerun (YouTube → NotebookLM) — 2026-04-11

## What happened
- I re-ran YouTube research for hedge fund roles / memos / risk / portfolio process.
- The search results skewed toward low-quality or adjacent content.
- NotebookLM ingestion currently has an instability: adding many sources via loop sometimes results in only 1 source being present.

## Best usable sources found (URLs)
From the better query (`hedge fund analyst investment memo template risk manager portfolio construction`):
- Macro trader levels/day-in-life: https://www.youtube.com/watch?v=2-oozMZ8Q1w
- HF junior analyst day-in-life: https://www.youtube.com/watch?v=kaCSCAAu3Rc
- HF portfolio manager day-in-life: https://www.youtube.com/watch?v=nG1jUA9f3-s
- How to pitch a stock (equity research): https://www.youtube.com/watch?v=7qd0Hzaw5nU
- Quant finance intro: https://www.youtube.com/watch?v=JVtUcM1sWQw

## Key extracted conclusion (reliable)
The strongest actionable extraction from the available sources is the **IC memo / stock pitch structure** (recommendation first, 3-part thesis, differentiated view vs consensus, valuation model, bull/bear, catalysts).

## Practical implication
We should not block our build on weak YouTube sourcing.
Instead:
1) Use the TOM/RACI/Cadence templates already created.
2) Use the IC packet template (already in vault) and improve it with the pitch structure.
3) Move forward to building the multi-agent org with strict output contracts.

## Blockers / fixes
- YouTube search quality depends heavily on query formulation.
- NotebookLM multi-source add appears flaky; use fewer sources or add them one-by-one and confirm `source list` after each.
