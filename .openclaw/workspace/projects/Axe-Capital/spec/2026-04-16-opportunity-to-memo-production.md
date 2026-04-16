# Opportunity To Memo Production Spec

**Date:** 2026-04-16
**Status:** Approved for autonomous implementation

---

## Goal

Finish the next layer of Axe Capital so it can discover opportunities outside the live IBKR portfolio, run the specialist stack on those opportunities, produce decision memos, and run as a local service after reboot.

---

## Product Flow

1. Step 5 refreshes the live IBKR portfolio.
2. Step 4 scans for opportunities outside the live IBKR holdings.
3. Step 7 takes the top opportunity candidates and runs:
   - Fundamental Analyst
   - Technical Analyst
   - Macro Strategist
   - Step 3 debate and memo
4. Step 3 runs a stricter decision chain:
   - Bull
   - Bear
   - Risk Manager
   - Compliance/Audit
   - CEO final decision
5. The dashboard/API can trigger the flow with `opportunities`.

---

## Rules

- Existing portfolio symbols come from `step6-dashboard/public/portfolio.json`, not a static profile table.
- Opportunity candidates already held in IBKR are excluded before memo generation.
- Candidate memos must include specialist reports when available.
- Risk Manager must produce an explicit gate, sizing constraints, scenario risks, and veto rationale.
- Compliance/Audit must list source coverage, missing evidence, assumption quality, and audit status.
- CEO receives Bull, Bear, Risk Manager, and Compliance/Audit outputs before deciding.
- No order execution is added. Robert still executes manually in IBKR.

---

## New Commands

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
python -m axe_orchestrator.cli run opportunities
python -m axe_orchestrator.cli run opportunities 3
```

Behavior:

- Runs portfolio refresh.
- Runs alpha scan.
- Reads `alpha-latest.json`.
- Selects top candidates not in the portfolio.
- Runs specialists and decision memo per selected ticker.
- Returns non-zero if any selected candidate fails.

---

## Production Runtime

Add user-systemd service files and an installer script:

- API service on port 8000.
- Dashboard service on port 5173.
- Monthly specialist timer.

The install script copies units to `~/.config/systemd/user/`, reloads the user daemon, enables API/dashboard startup, and enables the monthly specialist timer. It does not place trades.

