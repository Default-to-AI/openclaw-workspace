# Axe Capital Dashboard Workflow

## Operating model

The dashboard is file-first and API-enhanced.

- File-first means every panel should still render from artifacts in `public/`.
- API-enhanced means refresh actions and live trace streaming become available when Step 7 is running.

## Normal manual loop

1. Update source inputs if needed, especially the IBKR CSV.
2. Run refresh through Step 7 (`axe run all` or the refresh buttons once API is up).
3. Open the dashboard.
4. Review portfolio state, new alpha, hot news, agent traces, and archive entries.

## Artifact ownership

- Step 4 writes `alpha-latest.json`
- Step 2 writes `news-latest.json`
- Step 5 writes `portfolio.json` and `weekly-review-latest.json`
- Step 0/7 maintain `traces/` and `health.json`
- Step 7 appends operational notes to `decision-log.jsonl`

## UX principle

The dashboard should feel like a research operating surface, not a pile of disconnected widgets. Panels should answer:
- what changed,
- what matters,
- what is blocked,
- what needs Robert's decision.
