---
type: runbook
project: axe-capital
status: active
created: 2026-04-11
tags: [axe-capital, decision-log]
---

# Decision Log — Format

Each decision gets one entry file:
`YYYY-MM-DD__TICKER__action.md`

## Template

```markdown
---
type: decision
project: axe-capital
date: YYYY-MM-DD
ticker: TICKER
action: buy|sell|hold|increase|decrease
status: proposed|approved|rejected|executed|reverted
---

# Decision: TICKER — action

## TL;DR
- Thesis:
- Why now:
- What would change my mind (invalidation):
- Size:
- Risk checks: PASS/FAIL + why

## Inputs
- Sources:
- Key facts:
- Assumptions:

## Analysis
- Base case:
- Bear case:
- Bull case:

## Risk & constraints
- Max loss / stop logic:
- Exposure impact:
- Correlation / concentration:

## Execution plan
- Order type:
- Entry:
- Exit:
- Contingencies:

## Post-mortem (filled after)
- What happened:
- What we learned:
- Process change (if any):
```
