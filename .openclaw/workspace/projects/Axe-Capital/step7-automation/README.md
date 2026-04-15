# Axe Capital Step 7 — Automation & API

Step 7 is the operational control layer for Axe Capital.

## What lives here

- `axe_orchestrator/cli.py` — unified CLI entrypoint (`axe run alpha|news|portfolio|all`, `axe health`)
- `axe_orchestrator/api.py` — thin FastAPI backend for:
  - `GET /health`
  - `POST /refresh/{target}`
  - `GET /trace/stream/{run_id}` via SSE
- `axe_orchestrator/health.py` — artifact freshness generation for `step6-dashboard/public/health.json`
- `run_daily_refresh.sh` — cron-friendly wrapper that runs the orchestrator, syncs weekly review, and appends decision-log events

## Usage

### CLI

```bash
cd projects/Axe-Capital/step7-automation
python -m axe_orchestrator.cli run all
python -m axe_orchestrator.cli health
```

### API

```bash
cd projects/Axe-Capital/step7-automation
uvicorn axe_orchestrator.api:app --reload --port 8000
```

The dashboard proxies `/api/*` to port 8000 in local dev and falls back to static artifacts when the API is unavailable.

## Design notes

- The dashboard must remain readable from static files alone.
- Refresh endpoints are serialized with a lock to avoid overlapping runs.
- Trace SSE streams from trace files, which are now updated incrementally during agent runs.
- Health uses `generated_at` when present and file modification time as a fallback.
