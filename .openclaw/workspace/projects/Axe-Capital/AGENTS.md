# Axe Capital — Agent Instructions

## Package Structure

This is a Python monorepo with 11 steps:

| Step | Package | Description |
|------|---------|-------------|
| step0-shared | axe-core | Shared utilities (trace, paths, schemas) |
| step1-data-foundation | axe-coo | COO data connectors |
| step2-news | axe-news | RSS ingestion + LLM scorer |
| step3-debate-decision | axe-decision | Debate + decision layer |
| step4-alpha-hunter | axe-alpha | Alpha scanning |
| step5-portfolio-tracking | axe-portfolio | Portfolio tracker |
| step6-dashboard | — | React/Vite dashboard |
| step7-automation | axe-orchestrator | Orchestrator + FastAPI |
| step8-fundamental | axe-fundamental | Fundamental analyst |
| step9-technical | axe-technical | Technical analyst |
| step10-macro | axe-macro | Macro strategist |

## Running Packages

```bash
# Install/edit any step (must run from its directory)
for step in step0-shared step1-data-foundation step2-news step3-debate-decision step4-alpha-hunter step5-portfolio-tracking step8-fundamental step9-technical step10-macro; do
  (cd $step && uv pip install -e .)
done

# Run CLI entry points
axe                   # step7: orchestrator CLI (run alpha|news|portfolio|all|specialists|opportunities)
axe-alpha             # step4: alpha scanner
axe-news              # step2: news ingestion
axe-decision          # step3: run debate
axe-fundamental       # step8: fundamental analyst
axe-technical         # step9: technical analyst
axe-macro             # step10: macro strategist
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
- `.env` file at project root for API keys (ANTHROPIC_API_KEY, IBKR credentials)
- Live portfolio data pulled via IBKR API

## References

- Full project context: `CLAUDE.md`
- Dashboard workflow: `step6-dashboard/WORKFLOW.md`
- Specs: `spec/`, `plans/`, `runbooks/`

## Remaining Work

The following features are not yet implemented:
- `./scripts/dev.sh` single-command startup
- Scheduled refresh (cron during market hours)
- Decision/archive pruning rules
- Tailscale deployment documentation
