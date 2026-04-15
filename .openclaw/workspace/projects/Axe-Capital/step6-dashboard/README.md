# Axe Capital Dashboard

The Step 6 dashboard is the research surface for Axe Capital.

## Panels

1. Portfolio State
2. Watchlist & Targets
3. Alpha Opportunities
4. Hot News
5. Agent Status Board
6. Internal Dialogue Viewer
7. Decision Archive

## Data model

The UI renders pre-generated artifacts from `public/` and upgrades to API-backed controls when the backend is available.

Primary artifacts:
- `portfolio.json`
- `targets.json`
- `alpha-latest.json`
- `news-latest.json`
- `traces/index.json`
- `traces/<run-id>.json`
- `decision-log.jsonl`
- `health.json`

## Development

```bash
npm run dev
```

The Vite dev server proxies `/api/*` to `http://localhost:8000`.

## Backend pairing

Run the API from Step 7 when you want refresh buttons and live trace streaming:

```bash
cd ../step7-automation
uvicorn axe_orchestrator.api:app --reload --port 8000
```

If the API is unavailable, the dashboard still reads static artifacts directly.
