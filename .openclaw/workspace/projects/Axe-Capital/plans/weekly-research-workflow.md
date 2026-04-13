---
type: plan
project: axe-capital
status: active
created: 2026-04-11
tags: [axe-capital, ibkr, workflow]
---

# Weekly Research → Thesis → Approval Queue (Paper-First)

## Inputs you give me
- Universe scope: holdings-only OR holdings + watchlist
- Any themes you care about this week

## Pipeline (what I do)
1) Collect: prices/returns, earnings calendar, major news for holdings/watchlist.
2) Produce 3 lists:
   - **Keep / monitor** (nothing to do)
   - **Research candidates** (need a thesis)
   - **Action candidates** (potential trades)
3) For each Action candidate, write a decision log entry using the template.
4) Update the Approval Queue with 1–3 proposals.

## Output artifacts
- Approval queue: `02_Plans/approval-queue.md`
- Decision logs: `04_DecisionLog/YYYY-MM-DD__TICKER__action.md`

## Guardrails
- Paper-only by default.
- No action without invalidation + sizing + risk pass.
- If data is missing (financials, earnings date), mark as “Needs Input” instead of guessing.
