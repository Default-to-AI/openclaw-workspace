# Axe Capital — Agent Instructions

## Package Structure

This is a Python monorepo with 8 steps:

| Step | Package | Description |
|------|---------|-------------|
| step0-shared | axe-core | Shared utilities (trace, paths, schemas) |
| step1-data-foundation | axe-coo | COO data connectors |
| step2-news | axe-news | RSS ingestion + LLM scorer |
| step3-debate-decision | axe-decision | Debate + decision layer |
| step4-alpha-hunter | axe-alpha | Alpha scanning |
| step5-portfolio-tracking | axe-portfolio-tracking | Portfolio tracker |
| step6-dashboard | — | React/Vite dashboard |
| step7-automation | axe-orchestrator | Orchestrator + FastAPI |

## Running Packages

```bash
# Install/edit any step (must run from its directory)
uv pip install -e .

# Run CLI entry points
axe-coo-bundle        # step1: data bundler
axe-step2-analyze     # step1: step2 analysis
axe-step3-decide      # step1: step3 decisions
axe-news              # step2: news ingestion
axe-decision          # step3: run debate
axe-portfolio-review  # step5: portfolio review
axe                   # step7: orchestrator CLI
```

## Dashboard (step6-dashboard)

```bash
cd step6-dashboard
npm run dev        # Vite dev server on :5173
npm run build      # Production build to dist/
npm run lint       # ESLint
```

The dashboard reads static JSON from `step6-dashboard/public/`:
- `portfolio.json`, `targets.json`, `alpha-latest.json`, `news-latest.json`
- `traces/index.json`, `traces/<run-id>.json`
- `decision-latest.json`, `decisions/*.json`

## Backend Pairing

For live data + refresh buttons:

```bash
cd step7-automation
uv pip install -e ".[api]"
uvicorn axe_orchestrator.api:app --reload --port 8000
```

Dashboard proxies `/api/*` to `http://localhost:8000`.

## Development Notes

- All step* packages depend on `axe-core` (step0-shared) via editable path dependency
- Install step0-shared first: `cd step0-shared && uv pip install -e .`
- Then install other steps in any order
- `.env` file at project root for API keys
- Broker data symlinks at `dashboard/data/raw/` → Obsidian vault (read-only)

## References

- Full project context: `CLAUDE.md`
- Dashboard workflow: `step6-dashboard/WORKFLOW.md`
- Specs/plans: `spec/`, `plans/`, `runbooks/`
