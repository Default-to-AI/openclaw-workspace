# Axe Capital — Agent Instructions

## Package Structure

This is a Python monorepo with 11 steps:

| Step | Package | Description |
|------|---------|-------------|
| step0-shared | axe-core | Shared utilities (`Tracer`, paths, schemas, shared LLM helper) |
| step1-data-foundation | axe-coo | COO data connectors + step3 committee decision helper |
| step2-news | axe-news | RSS ingestion + scoring |
| step3-debate-decision | axe-decision | Debate + CEO decision layer |
| step4-alpha-hunter | axe-alpha | Alpha scanning |
| step5-portfolio-tracking | axe-portfolio | Portfolio tracker with IBKR live -> Flex Query -> cached CSV fallback |
| step6-dashboard | — | React/Vite dashboard |
| step7-automation | axe-orchestrator | Orchestrator + FastAPI + committee streaming |
| step8-fundamental | axe-fundamental | Fundamental analyst |
| step9-technical | axe-technical | Technical analyst |
| step10-macro | axe-macro | Macro strategist |

## Running Packages

```bash
# Install/edit any step (must run from its directory)
for step in step0-shared step1-data-foundation step2-news step3-debate-decision step4-alpha-hunter step5-portfolio-tracking step8-fundamental step9-technical step10-macro step7-automation; do
  (cd "$step" && uv pip install -e .)
done

# Run CLI entry points
axe                   # step7: orchestrator CLI
axe-alpha             # step4: alpha scanner
axe-news              # step2: news ingestion
axe-decision          # step3: debate + decision
axe-fundamental       # step8: fundamental analyst
axe-technical         # step9: technical analyst
axe-macro             # step10: macro strategist
```

## Dashboard

```bash
cd step6-dashboard
npm run dev
npm run build
npm run lint
```

The dashboard reads artifacts from `step6-dashboard/public/`, including:
- `portfolio.json`, `position-state.json`, `weekly-review-latest.json`
- `alpha-latest.json`, `news-latest.json`
- `decision-latest.json`, `decisions/*.json`
- `health.json`
- `traces/index.json`, `traces/<run-id>.json`

Current UI sections:
- `Overview` for daily brief
- `Portfolio`
- `Research`
- `Operations`
- `Committee` for live committee runs and playbook output

## Backend Pairing

For health, refresh buttons, trace SSE, and committee runs:

```bash
cd step7-automation
uv pip install -e ".[api]"
uvicorn axe_orchestrator.api:app --reload --port 8000
```

Dashboard API usage:
- `/api/health`
- `/api/refresh/{target}`
- `/api/trace/stream/{run_id}`
- `/api/runs/{ticker}`
- `/api/runs/{run_id}/stream`

## Portfolio Data Rules

- Preferred source order is `IBKR live -> Flex Query -> cached CSV`.
- `portfolio.json` includes `data_source`; do not remove it.
- `weekly-review-latest.json` is dual-written to the portfolio reports area and dashboard public artifacts.
- Flex statement rows may contain duplicate symbols across accounts; they must be aggregated by symbol.
- Cash handling prefers `BASE`, then `USD`, then raw totals to avoid double-counting.

## Development Notes

- Install `step0-shared` first because other packages depend on `axe-core`.
- Specialist agents now share the common OpenAI JSON helper in `step0-shared/axe_core/llm.py`.
- CEO actions are more granular than simple buy/sell: `BUY`, `ADD`, `HOLD`, `TRIM`, `SELL`, `TIGHTEN_STOP`, `LOOSEN_STOP`, `REBALANCE`, `WATCH`.
- `scripts/axe-dev.sh` is the preferred local launcher and now surfaces portfolio source readiness.
- `.env` at repo root should contain `OPENAI_API_KEY` plus IBKR and Flex credentials when live portfolio sync is needed.

## References

- Full project context: `CLAUDE.md`
- Project status and next milestones: `ROADMAP.md`
- Description for external/project context: `docs/description-axe-capital.md`
- Specs and plans: `spec/`, `plans/`, `runbooks/`

## Remaining Work

The following items are still open:
- Scheduled refresh / market-hours automation
- Trace and decision archive pruning rules
- Risk manager and compliance/audit agents
- Production deployment and operator runbooks
