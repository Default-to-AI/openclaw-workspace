# Axe Capital — Agent Ground Rules

## Directory Boundary Rule

| Location | Purpose |
|---|---|
| `projects/Axe-Capital/` | **Everything Axe Capital builds** — code, normalized data, reports, specs, plans, runbooks, decision logs, sources |
| `obsidian-vault/` (Vault) | **Robert's personal notes only** — human-written research, journal entries, reading notes |

**Never write agent output into the Obsidian vault.** This includes: normalized CSVs, JSON reports, Python scripts, generated markdown docs, snapshots, memos, or any file produced by an agent or pipeline run.

## Broker Data (Read-Only Inputs)

The system prefers live portfolio data from IBKR/TWS, but now supports a fallback chain:
- IBKR live via gateway/TWS
- IBKR Flex Query snapshot
- Cached CSV as last resort

Historical exports can be stored in the vault:
- IBKR statements → `Finance/raw/IBKR/Statements/`
- Portfolio snapshots → `Finance/raw/Portfolio/`

The system reads broker data via `.env` configured IBKR and Flex credentials.

## Project Structure

```
projects/Axe-Capital/
  step0-shared/            # axe_core shared package
  step1-data-foundation/   # axe_coo data pipeline
  step2-news/              # axe_news RSS + LLM scorer
  step3-debate-decision/   # axe_decision debate layer
  step4-alpha-hunter/      # axe_alpha alpha scanner
  step5-portfolio-tracking/ # axe_portfolio tracker
  step6-dashboard/        # Dashboard UI (artifact home: public/)
    public/               # All artifacts (portfolio.json, weekly-review-latest.json, health.json, traces/, etc.)
  step7-automation/       # axe_orchestrator CLI + FastAPI + committee SSE
  step8-fundamental/     # axe_fundamental analyst
  step9-technical/       # axe_technical analyst
  step10-macro/          # axe_macro strategist
  spec/                  # Vision, strategy, architecture, org, risk docs
  plans/                 # Implementation plans, roadmaps
  runbooks/              # Operational runbooks for agent workflows
  ops/                   # systemd services, install scripts
```

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health

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
