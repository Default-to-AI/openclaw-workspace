# Axe Capital Step 7 — Automation

Goal: produce all dashboard/public artifacts on a schedule, with a kill-switch and a full audit trail.

Phase 1 (now): local cron-friendly scripts that:
- run the portfolio tracker (step5) to refresh `portfolio.json` and `reports/weekly-review-latest.json`
- sync the weekly review into the dashboard `public/`
- write a simple `health.json` heartbeat
- append to `decision-log.jsonl`

Live trading stays manual approval.

