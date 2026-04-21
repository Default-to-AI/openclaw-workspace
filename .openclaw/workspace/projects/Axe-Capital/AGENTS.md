# Axe Capital — AGENTS.md

## Purpose Of This File

This file is the repo-specific operating contract for coding agents working on Axe Capital.

Use it for:
- agent behavior in this repository
- project-specific guardrails
- stable architecture and data-contract warnings
- fast orientation to the project

Do not use it for:
- roadmap status
- milestone tracking
- task backlog
- release notes
- recent change summaries

Those belong in the project source-of-truth files listed below.

## Project Brief

Axe Capital is a hedge-fund-style multi-agent research platform for public equities.

The core product is not the dashboard itself. The real system is the pipeline:
- ingest market, portfolio, and news data
- run specialist analysis
- run debate and decision synthesis
- produce a CEO decision and position playbook
- expose artifacts in the dashboard for the operator

The operator executes trades manually. The system is research and decision support, not auto-trading.

## Source Of Truth

Before making planning or documentation claims, read the right file:

- `ROADMAP.md`
  Use for project status, milestones, tech debt, and next priorities.
- `/home/tiger/.openclaw/workspace/obsidian-vault/Axe_Capital_Tasks.md`
  Use for the active task backlog and session-level outstanding work.
- `docs/description-axe-capital.md`
  Use for the current product description and high-level system overview.
- `spec/`
  Use for architecture, org-chart, risk, and design intent.
- `CLAUDE.md`
  Use for adjacent repo context and broader working rules.

Do not restate changing roadmap or task state in `AGENTS.md`.

## Repo Boundaries

- Keep all Axe Capital code, generated reports, artifacts, runbooks, and project docs inside `projects/Axe-Capital/`.
- Do not write generated project output into the Obsidian vault.
- Treat the vault as human planning and knowledge space, not as the runtime artifact store.

## Repo Shape

High-level layout:

- `step0-shared/`
  Shared utilities and core helpers.
- `step1-data-foundation/` to `step10-macro/`
  Pipeline packages and agents.
- `step6-dashboard/`
  React dashboard.
- `step7-automation/`
  FastAPI backend and orchestration layer.
- `spec/`, `plans/`, `runbooks/`
  Project docs and execution docs.
- `scripts/`
  Repo-local helper scripts.

## Agent Behavior

- Make surgical changes. Touch only what the task requires.
- Preserve existing architecture unless the task explicitly calls for structural change.
- Prefer updating the true source-of-truth file over duplicating information into multiple docs.
- Do not silently rewrite project intent. If a change affects product behavior or architecture, update the relevant spec, roadmap, or description file deliberately.
- Verify important claims with code, docs, or artifacts in the repo before stating them.
- Treat generated artifacts, runtime output, and source files differently. Do not mix them casually in the same change without reason.
- If the task concerns open work or priorities, consult the vault task file rather than inferring from stale docs.

## Critical Contracts

### Artifact Contract

`step6-dashboard/public/` is the primary artifact boundary between the Python pipeline and the dashboard.

Agents should assume this directory is a contract surface. Be careful when changing:
- `portfolio.json`
- `weekly-review-latest.json`
- `decision-latest.json`
- `health.json`
- `position-state.json`
- `traces/index.json`
- trace payload structure

If an artifact schema changes, update all affected readers in the dashboard and backend.

### API/UI Coupling

The dashboard depends on backend routes in `step7-automation/axe_orchestrator/api.py` and client code in `step6-dashboard/src/lib/api.js`.

Do not change API routes, request shapes, or SSE behavior without updating the frontend callers in the same change.

### Decision Vocabulary

The CEO action vocabulary is a shared contract across backend logic and UI rendering.

When changing action names or semantics, keep the following aligned:
- `step3-debate-decision/axe_decision/cli.py`
- `step7-automation/axe_orchestrator/committee_orchestrator.py`
- committee/dashboard UI components

### Portfolio Ingestion

Portfolio ingestion currently follows a fallback chain:
- IBKR live
- Flex Query
- cached CSV

Preserve that behavior unless the task explicitly changes it.

Be careful with:
- `data_source` in portfolio artifacts
- duplicate-symbol aggregation across accounts
- cash handling and double-counting

## Documentation Rules

- `AGENTS.md` should stay stable and behavioral.
- `ROADMAP.md` tracks status and priorities.
- `docs/description-axe-capital.md` explains what the project is.
- The vault task file tracks open tasks.

If a request is “update the docs,” choose the file based on purpose instead of updating everything.

## Working Style For This Repo

- Prefer small, defensible diffs over broad cleanup.
- Do not remove “developer-looking” panels, routes, or files unless the task explicitly asks for product cleanup.
- When touching dashboard behavior, consider both static artifact mode and API-backed mode.
- When touching orchestration, prefer preserving traceability and debuggability over cleverness.
- Before claiming something is fixed, run the lightest real verification available.

## References

- [CLAUDE.md](/home/tiger/.openclaw/workspace/projects/Axe-Capital/CLAUDE.md)
- [ROADMAP.md](/home/tiger/.openclaw/workspace/projects/Axe-Capital/ROADMAP.md)
- [description-axe-capital.md](/home/tiger/.openclaw/workspace/projects/Axe-Capital/docs/description-axe-capital.md)
- [Axe_Capital_Tasks.md](/home/tiger/.openclaw/workspace/obsidian-vault/Axe_Capital_Tasks.md)
