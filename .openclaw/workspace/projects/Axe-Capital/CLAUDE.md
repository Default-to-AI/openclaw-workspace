# Axe Capital — Agent Ground Rules

## Directory Boundary Rule

| Location | Purpose |
|---|---|
| `projects/Axe-Capital/` | **Everything Axe Capital builds** — code, normalized data, reports, specs, plans, runbooks, decision logs, sources |
| `obsidian-vault/` (Vault) | **Robert's personal notes only** — human-written research, journal entries, reading notes |

**Never write agent output into the Obsidian vault.** This includes: normalized CSVs, JSON reports, Python scripts, generated markdown docs, snapshots, memos, or any file produced by an agent or pipeline run.

## Broker Data (Read-Only)

Fallback order: IBKR live → Flex Query → cached CSV. Credentials via `.env`. Vault storage: `Finance/raw/IBKR/Statements/` and `Finance/raw/Portfolio/`.

## Project Structure

Key modules: `step0-shared` (axe_core), `step1` (axe_coo), `step2` (axe_news), `step3` (axe_decision), `step4` (axe_alpha), `step5` (axe_portfolio), `step6-dashboard` (React UI + `public/` artifacts), `step7-automation` (axe_orchestrator FastAPI + committee SSE), `step8-10` (fundamental/technical/macro). Docs in `spec/`, `plans/`, `runbooks/`.

## Current Product Reality

- The dashboard is no longer just static panels plus manual refresh. It now has a live `Committee` tab that starts a ticker-specific run and streams analyst/debate/CEO/playbook events over SSE.
- `step7-automation/axe_orchestrator/api.py` is the backend entrypoint for health, refresh, trace streaming, and committee run streaming.
- `step7-automation/axe_orchestrator/committee_orchestrator.py` coordinates specialist analysis, debate synthesis, CEO action validation, and position playbook generation.
- Shared LLM JSON calls live in `step0-shared/axe_core/llm.py`; use that helper instead of duplicating OpenAI client code in individual agents.
- Portfolio artifacts must preserve the `data_source` field because the UI now distinguishes `IBKR live`, `Flex Query (T+1)`, and stale fallback snapshots.
- `docs/MISSION_LOG.md` was removed; use `ROADMAP.md`, `spec/`, `plans/`, and the dashboard/public artifacts as the source of current project state.

## Operating Constraints

- Treat `step6-dashboard/public/` as the artifact contract between Python pipelines and the React UI.
- Do not remove or rename current API routes without updating the dashboard client in `step6-dashboard/src/lib/api.js`.
- When modifying CEO action logic, keep the extended action vocabulary aligned across:
  - `step3-debate-decision/axe_decision/cli.py`
  - `step7-automation/axe_orchestrator/committee_orchestrator.py`
  - dashboard committee UI components
- When modifying portfolio ingestion, preserve the current fallback order and avoid cash double-counting across accounts/currencies.

## Compact Instructions

When compacting this session, preserve: active ticker or pipeline step; modified file paths with line ranges; error-fix sequences; open decisions and unresolved TODOs. Include the next concrete step.
