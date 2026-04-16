# Axe Capital Prototype Launch

This is the shortest path to seeing the prototype alive.

## Goal

Bring up:

- the Step 7 API backend
- the Step 6 dashboard UI
- then run a refresh or specialist baseline to populate fresh artifacts

---

## Normal User Startup

Start TWS or IB Gateway first, log in to Interactive Brokers, and leave it running.

If services are installed, open:

```text
http://localhost:5173
```

If services are not installed yet, run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital
./step7-automation/start_prototype.sh
```

Expected:

- Step 7 API starts on port 8000
- Step 6 dashboard starts on port 5173
- logs are written to `step7-automation/logs/`

Open:

```text
http://localhost:5173
```

---

## Install Reboot-Surviving Services

Run once:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital
bash ops/install_user_services.sh
```

After that, the API and dashboard are enabled as user services and the monthly specialist baseline is enabled as a timer.

Useful commands:

```bash
systemctl --user status axe-api.service
systemctl --user status axe-dashboard.service
systemctl --user list-timers axe-monthly-specialists.timer
journalctl --user -u axe-api.service -f
journalctl --user -u axe-dashboard.service -f
```

---

## Refresh Current Artifacts

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
python -m axe_orchestrator.cli run all
```

Expected:

- portfolio / alpha / news runs execute
- `health.json` refreshes
- traces refresh

---

## First Specialist Baseline / Monthly Specialist Rerun

Run this after TWS or IB Gateway is connected:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
python -m axe_orchestrator.cli run specialists
```

Expected:

- Step 5 refreshes the IBKR portfolio
- Fundamental, Technical, and Macro reports run for every positive-position symbol in `portfolio.json`
- reports are written under `step6-dashboard/public/analyst-reports/`
- `step6-dashboard/public/analyst-reports/index.json` points to the latest reports

---

## Opportunity-To-Memo Pipeline

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
python -m axe_orchestrator.cli run opportunities
```

Or run the top three candidates:

```bash
python -m axe_orchestrator.cli run opportunities 3
```

Expected:

- Step 5 refreshes the IBKR portfolio
- Step 4 scans for outside-portfolio opportunities
- top candidates not already held in IBKR get specialist reports
- Step 3 writes decision memos with Bull, Bear, Risk Manager, Compliance/Audit, and CEO sections

---

## Manual Developer Startup

If the one-command launcher needs debugging, run the API and dashboard separately.

Terminal 1:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
uvicorn axe_orchestrator.api:app --reload --port 8000
```

Terminal 2:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step6-dashboard
npm run dev -- --host 0.0.0.0 --port 5173
```

## If Python Path Is Weird

Use the project virtualenv explicitly:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
../.venv/bin/python -m axe_orchestrator.cli run all
```

or use the project virtualenv explicitly for `uvicorn` too.

---

## What To Send Back If Something Breaks

Send exactly:

1. API terminal output
2. Dashboard terminal output
3. Refresh command output
4. Screenshot of the UI if it loads

No summaries. Raw errors are better.
