# Axe Capital — Taskboard

> Source of truth for build execution tasks (Dashboard + Automation).
> This file is intentionally small. Keep tasks atomic.
> Code and engineering live in `projects/Axe-Capital/` — this is the knowledge and task layer.

## Now (current focus)
- [x] (Dashboard) Panel 2: finalize semantics for % rules (avg-cost vs last) and encode in UI copy + calculations ✅ 2026-04-16
- [x] (Dashboard) Panel 7: Decision Archive UI reading decision JSON files (list + filters + details) ✅ 2026-04-16

## Next (dashboard panels)
- [x] (Dashboard) Panel 3: Alpha Opportunities UI + alpha feed JSON contract ✅ 2026-04-16
- [x] (Glue) Standardize data contracts in `/public/*.json` (portfolio, targets, decisions, alpha, debate) ✅ 2026-04-16
- [x] (Dashboard) Panel 6: Internal Dialogue Viewer (debate transcript explorer) ✅ 2026-04-16

## Backend (only when needed)
- [x] (Backend) Minimal FastAPI server to serve: hot news, agent status, decision store query ✅ 2026-04-16
- [x] (Dashboard) Panel 4: Hot News (scored feed, position tagging) — requires backend ✅ 2026-04-16
- [x] (Dashboard) Panel 5: Agent Status Board (state machine + last action) — requires backend ✅ 2026-04-16

## Automation (Step 7)
- [x] (Cron) Morning scan at 9:00 AM ET ✅ 2026-04-16
- [x] (Cron) Alpha Hunter nightly scan ✅ 2026-04-16
- [x] (Cron) Position monitor every 30m during market hours ✅ 2026-04-16
- [x] (Cron) Weekly CEO health memo on Sunday ✅ 2026-04-16
- [x] (Telegram) Alerts: stop proximity, new alpha, memo ready ✅ 2026-04-16
- [x] (Report) Monthly PDF report generation + Telegram delivery ✅ 2026-04-16

## Deployment
- [x] (Deploy) Tailscale deployment + runbook ✅ 2026-04-16
