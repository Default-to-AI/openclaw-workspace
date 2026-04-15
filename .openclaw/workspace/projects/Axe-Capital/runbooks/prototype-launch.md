# Axe Capital — Prototype Launch

This is the shortest path to seeing the prototype alive.

## Goal
Bring up:
- the Step 7 API backend
- the Step 6 dashboard UI
- then run a refresh to populate fresh artifacts

---

## Terminal 1 — API

```bash
cd projects/Axe-Capital/step7-automation
uvicorn axe_orchestrator.api:app --reload --port 8000
```

Expected:
- server starts on port 8000
- no import/module errors

---

## Terminal 2 — Dashboard

```bash
cd projects/Axe-Capital/step6-dashboard
npm run dev -- --host 0.0.0.0 --port 5173
```

Expected:
- Vite starts
- dashboard available locally on port 5173
- `/api/*` routes proxy to port 8000

---

## Terminal 3 — Generate fresh data

```bash
cd projects/Axe-Capital/step7-automation
python -m axe_orchestrator.cli run all
```

Expected:
- portfolio / alpha / news runs execute
- `health.json` refreshes
- traces refresh

---

## If Python path is weird

Try:

```bash
cd projects/Axe-Capital/step7-automation
../.venv/bin/python -m axe_orchestrator.cli run all
```

or use the project virtualenv explicitly for uvicorn too.

---

## What to send back if something breaks

Send exactly:
1. API terminal output
2. Dashboard terminal output
3. Refresh command output
4. Screenshot of the UI if it loads

No summaries. Raw errors are better.
