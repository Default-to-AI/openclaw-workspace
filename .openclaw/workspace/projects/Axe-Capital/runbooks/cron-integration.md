# Axe Capital — Cron Integration Path

This is the endgame integration path for scheduled refreshes. Do not enable until the local manual flow is stable.

## Recommended cron target

Call the Step 7 wrapper, not individual agents.

```bash
cd /path/to/projects/Axe-Capital/step7-automation && ./run_daily_refresh.sh
```

## Suggested schedule

### Daily pre-market refresh
Run before Robert's review window.

```cron
30 14 * * 1-5 cd /path/to/projects/Axe-Capital/step7-automation && ./run_daily_refresh.sh >> /path/to/projects/Axe-Capital/logs/cron.log 2>&1
```

Adjust for the machine timezone and the desired US market pre-open timing.

## Principles

- One cron entry should call one owner script.
- The script should regenerate health after runs.
- The script should append a decision-log note for start and completion.
- Do not schedule raw per-agent commands independently unless debugging.

## Before enabling

- Confirm `axe run all` succeeds cleanly.
- Confirm `news-latest.json`, `alpha-latest.json`, `portfolio.json`, and `traces/index.json` refresh.
- Confirm the dashboard reads fresh artifacts after the scheduled run.
