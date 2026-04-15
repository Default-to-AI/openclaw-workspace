# Axe Capital — Current State & Next Steps (2026-04-16)

## Why this document exists

You asked: *“Where are we, what’s missing, and how do we get to a fully functional dashboard app?”*

This file is the single “you are here” truth that ties together:
- the long-form plans/specs in `spec/` and `plans/`
- the actual code reality in `step0..step7`
- the minimum remaining work to make Axe Capital feel like a real product (not a terminal demo)

---

## What Axe Capital is (product definition)

**Axe Capital = an agent pipeline that writes artifacts + traces, plus a dashboard that renders them.**

- Agents run in Python (Step 1–5 + Step 3), producing JSON artifacts under `step6-dashboard/public/`
- The dashboard (Step 6) renders those artifacts file-first
- The API (Step 7) is optional but unlocks:
  - refresh buttons
  - health endpoint
  - trace streaming (SSE)

**Non-goal (explicit):** no live order execution.

---

## What works today (facts)

### End-to-end “portfolio → dashboard artifact”
- [x] Live IBKR ingest via TWS using `ib_async` (read-only)
- [x] Multi-account support via `AXE_IBKR_ACCOUNTS=...`
- [x] Writes `step6-dashboard/public/portfolio.json` (dashboard contract)
- [x] Writes weekly review JSON + normalized CSV snapshots
- [x] Trace emitted for runs under `step6-dashboard/public/traces/`

### Dashboard (Step 6) “file-first UI”
- [x] Dashboard renders from static artifacts in `step6-dashboard/public/`
- [x] Can run without API (read-only mode)

### API/Orchestrator (Step 7) “ops layer”
- [x] `POST /refresh/{target}` triggers agent runs
- [x] `GET /health` reports freshness
- [x] `GET /trace/stream/{run_id}` streams trace events

---

## How you run it like an app (current, manual)

### Dev dashboard
From `projects/Axe-Capital/step6-dashboard/`:
```bash
npm run dev
```
Dashboard: `http://localhost:5173`

### Dev API
From `projects/Axe-Capital/step7-automation/`:
```bash
uvicorn axe_orchestrator.api:app --reload --port 8000
```
API: `http://localhost:8000`

### Refresh portfolio from the API-backed dashboard
Click “Portfolio” in the dashboard “System State” bar (or `POST /refresh/portfolio`).

---

## What’s missing (to be “fully functional” as described)

This is the punch list that prevents Axe from feeling like a real product you can rely on daily.

### 1) Single-command startup (highest friction today)
**Missing:** one command to start the whole system (API + dashboard), and optionally keep them running.

- [ ] A repo command like `./scripts/dev.sh` or `make dev` that starts:
  - Step 7 API on `:8000`
  - Step 6 dashboard on `:5173`
  - shows URLs + basic health checks
- [ ] A “production-ish” runner option:
  - systemd services OR a simple `tmux` runner OR docker-compose (pick one)

### 2) “Always-on” refresh without terminal use
**Missing:** predictable refresh cadence + UI that tells you what’s stale and why.

- [ ] scheduled refresh during market hours (portfolio every N minutes)
- [ ] scheduled alpha/news refresh (hourly or daily)
- [ ] clear “broker disconnected / using stale data” UI states (not just generic failure)

### 3) Artifact hygiene (the app needs to stay clean)
**Missing:** retention policies and consistent artifact contracts.

- [ ] trace pruning (keep last N runs per agent)
- [ ] decision/archive pruning rules (or paging/search)
- [ ] stable artifact schema versioning (so UI doesn’t break when we evolve payloads)

### 4) “Research platform” pipeline is incomplete (big feature gap)
The roadmap/specs describe a hedge-fund org model (specialists → debate → memo).
Right now, the specialist agents are the largest missing capability.

- [ ] Fundamental Analyst agent (writes a report artifact)
- [ ] Technical Analyst agent (writes a report artifact)
- [ ] Macro Strategist agent (writes a report artifact)
- [ ] Wire those reports into bull/bear debate and the final memo

### 5) Deployment & access model (so you don’t babysit it)
You already have Tailscale in play; Axe should leverage it consistently.

- [ ] decide “where it lives”:
  - same machine as TWS (Windows/WSL), OR
  - Linux host that connects to TWS over Tailscale
- [ ] pin and document the config (env file + runbook)

---

## What we just finished (last milestone)

**IBKR live dashboard integration is now working with:**
- correct market prices / P&L (primed via account updates)
- multi-account pull using `AXE_IBKR_ACCOUNTS`
- read-only safety boundary preserved

Reference runbook: `runbooks/ibkr-live-dashboard-integration.md`

---

## Recommended next milestone (to avoid “not going anywhere”)

If the goal is “full-on app/dashboard”, the next milestone should be **operational**, not “more agents”.

### Milestone: “Axe boots like an app”
Definition of done:
- [ ] `./scripts/dev.sh` (or `make dev`) starts API + dashboard
- [ ] `./scripts/refresh.sh portfolio|all` exists and prints clear success/failure
- [ ] dashboard shows clear status if API is down (already partially true) and if refresh is in progress
- [ ] portfolio auto-refresh runs on schedule when market is open (configurable)

Only after that, build the missing specialist agents and wire them into step3.

---

## Next actions I can take autonomously (pick one)

1) **App-mode sprint (recommended):** add `scripts/dev.sh`, `scripts/run_api.sh`, `scripts/run_dashboard.sh`, and `scripts/schedule_refresh.sh` + update runbooks.

2) **Research-pipeline sprint:** implement the 3 specialist agents (fundamental/technical/macro) + feed their reports into step3 debate.

Reply with `1` or `2`.

