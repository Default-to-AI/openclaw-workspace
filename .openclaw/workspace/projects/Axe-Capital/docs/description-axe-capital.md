# Axe Capital — Project Description

> **Hedge-fund-style multi-agent research platform** that hunts for market-beating opportunities using autonomous AI agents, adversarial debate, and full audit trails.

---

## Overview

Axe Capital is a Python + React monorepo that simulates a hedge fund's organizational structure using autonomous AI agents. Each agent fills a role in a traditional fund org chart — CEO, COO, Portfolio Manager, Risk Manager, Analysts — and together they form a pipeline that:

1. **Ingests data** from RSS feeds, SEC filings, yfinance, and Interactive Brokers
2. **Runs independent analysis** via specialist agents (fundamental, technical, macro)
3. **Conducts adversarial debate** (bull vs bear on each opportunity)
4. **Produces CEO decisions and position playbooks** for the operator to execute manually on IBKR
5. **Maintains a full audit trail** via structured trace events

**Core thesis:** Retail investors can't do exhaustive multi-source research. Axe Capital's edge is **depth, speed, and adversarial structure** — surfacing the 3–5 best opportunities per month that retail misses, not 20 mediocre trades.

**North star metric:** IBKR portfolio outperforms SPY on a rolling 12-month basis.

---

## Architecture — 11-Step Pipeline

The system is organized as a monorepo of installable Python packages (steps 0–5, 7–10) and a React/Vite frontend (step 6):

| Step | Package | Role | Status |
|------|---------|------|--------|
| **step0-shared** | `axe-core` | Shared utilities — tracing, paths, schemas, shared LLM helper | ✅ Built |
| **step1-data-foundation** | `axe-coo` | COO — data connectors (IBKR, market data) | ✅ Built |
| **step2-news** | `axe-news` | RSS ingestion + LLM-based relevance scoring | ✅ Built |
| **step3-debate-decision** | `axe-decision` | Bull vs Bear debate → CRO → CEO decision flow | ✅ Built |
| **step4-alpha-hunter** | `axe-alpha` | Alpha scanning (SEC filings, yfinance) | ✅ Built |
| **step5-portfolio-tracking** | `axe-portfolio` | Portfolio tracker with `IBKR live -> Flex Query -> cached CSV` fallback | ✅ Built |
| **step6-dashboard** | React/Vite | Multi-tab UI with overview, research, ops, and live committee room | ✅ Built |
| **step7-automation** | `axe-orchestrator` | CLI + FastAPI backend + SSE streams | ✅ Built |
| **step8-fundamental** | `axe-fundamental` | Fundamental analyst agent | ✅ Built |
| **step9-technical** | `axe-technical` | Technical analyst agent | ✅ Built |
| **step10-macro** | `axe-macro` | Macro strategist agent | ✅ Built |

---

## Agent Org Chart

Modeled after a real hedge fund with clear roles and contracts:

```
                          ┌─────────┐
                          │   CEO   │  Final decision-maker
                          └────┬────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
        ┌─────┴─────┐   ┌─────┴─────┐   ┌──────┴──────┐
        │  COO/CFO   │   │ Portfolio  │   │    Risk     │
        │            │   │  Manager   │   │  Manager    │
        └────────────┘   └───────────┘   └─────────────┘
              │
    ┌─────────┼──────────┬──────────────┐
    │         │          │              │
┌───┴───┐ ┌──┴───┐ ┌────┴────┐ ┌──────┴──────┐
│ Fund. │ │ Tech │ │  Macro  │ │ Compliance  │
│Analyst│ │Analyst│ │Strategist│ │   /Audit   │
└───────┘ └──────┘ └─────────┘ └────────────┘
```

| Agent | Package | Function |
|-------|---------|----------|
| **CEO** | step3 | Final decision-maker — actions with rationale, sizing, invalidation |
| **COO/CFO** | step1 | Process management, capital allocation, exposure checks |
| **Portfolio Manager** | step5 | Portfolio construction, concentration, diversification |
| **Risk Manager** | step3 (CRO) | Risk limits, drawdown, correlation. Can veto. |
| **Fundamental Analyst** | step8 | Business quality, earnings, balance sheet, valuation |
| **Technical Analyst** | step9 | Market structure, entry/exit levels, trend confirmation |
| **Macro Strategist** | step10 | Rates, USD, liquidity, sector rotation, regime |
| **Compliance/Audit** | — | Sources, assumptions, audit trail *(not yet built)* |

### Decision Pipeline Flow

```
ticker → [Fundamental] → [Technical] → [Macro]
                    ↓
              Bull + Bear (with analyst inputs)
                    ↓
                  CRO → CEO → Position Playbook
```

---

## Data Pipeline

```
[RSS feeds]        [SEC EDGAR, yfinance]      [IBKR live / Flex / CSV]
     │                     │                           │
     ▼                     ▼                           ▼
  axe_news           axe_alpha                   axe_portfolio
                                                     │
                       ┌─────────────────────────────┴─────────────────────────────┐
                       ▼                                                           ▼
       specialist analysts (fundamental / technical / macro)                 weekly review
                       │
                       ▼
                Bull → Bear → CRO → CEO → Playbook
                       │
                       ▼
              step6-dashboard/public/ artifacts
                       │
              ┌────────┴────────┐
              ▼                 ▼
       React Dashboard      FastAPI + SSE
```

Each agent writes structured JSON artifacts to `step6-dashboard/public/`. The dashboard reads these files directly for static rendering, and proxies `/api/*` to the FastAPI backend for live refresh operations.

## Dashboard

The frontend is a React/Vite application organized around five operational tabs:
- **Overview** — daily brief combining portfolio state, decision output, and news
- **Portfolio** — targets / watchlist context
- **Research** — alpha opportunities, analyst reports, decision archive
- **Operations** — approval queue, weekly review, health, trace viewer
- **Committee** — live manual committee run with streamed analyst/debate/CEO/playbook events

Notable current UI behavior:
- Portfolio panel shows signed P&L formatting and alert legend (`RED`, `YELLOW`, `GREEN`)
- Weekly review labels SPY comparison metrics explicitly and formats USD vs percent fields correctly
- Sidebar supports targeted refresh actions: `all`, `portfolio`, `specialists_decide`, `alpha`, `news`
- Health and trace views are served from FastAPI when available, with file fallback for artifacts

## Committee Room

The newest workflow is the live committee room:

1. Operator selects a ticker from current portfolio holdings or enters a custom symbol
2. Operator chooses `position_review` or `new_position`
3. Backend builds context from portfolio state, recent news, and market data
4. Fundamental, technical, and macro specialists emit structured events
5. Debate / CRO / CEO stages stream into the UI live
6. A final position playbook is generated with key levels, stop, target, and review trigger

The committee backend exposes:
- `POST /api/runs/{ticker}` to start a run
- `GET /api/runs/{run_id}/stream` for SSE event streaming
- `GET /api/trace/stream/{run_id}` for artifact trace streaming

---

## Investor Profile Integration

The system is deeply personalized around the operator's actual financial situation:

- **IBKR active capital:** ~$120K across 13 positions 
- **Total net worth:** ~$216K across IBKR, managed portfolio, pension, hishtalmut, and gemel accounts
- **Investor psychology:** Aggressive accumulator — buys dips, no panic selling, conviction-driven

### Hard-Coded Decision Rules

Agents follow codified constraints:

| Rule | Detail |
|------|--------|
| **Max new position** | 15% of IBKR NAV (~$18K) |
| **Min position size** | $2,000 (below this, fees eat alpha) |
| **Cash floor** | Always maintain ≥ $5,000 liquid |
| **Stop-loss** | Mandatory on every new entry (default −10%) |
| **No leverage** | No margin, no options unless explicitly approved |
| **Hishtalmut priority** | Before any new trade, check if tax-advantaged account is maxed |
| **VIX regime** | Position sizing adjusts based on VIX level (<15 normal, >35 accumulation mode) |
| **Conviction threshold** | Weighted score ≥ 6.5/10 to proceed, ≥ 8.0 for high conviction |

### CEO Action Vocabulary

The CEO layer now supports more than simple buy/sell decisions:
- `BUY`
- `ADD`
- `HOLD`
- `TRIM`
- `SELL`
- `TIGHTEN_STOP`
- `LOOSEN_STOP`
- `REBALANCE`
- `WATCH`

### Scoring Weights

| Input | Weight |
|-------|--------|
| Fundamental score | 35% |
| Macro score | 25% |
| Technical score | 20% |
| Sentiment score | 20% |

---

## Development Workflow

### Prerequisites

- Python 3.11+ with `uv` package manager
- Node.js 18+ with npm
- API keys in `.env` (`OPENAI_API_KEY`, IBKR live credentials, Flex credentials as needed)

### Quick Start

```bash
# Install all Python packages (from project root)
for step in step0-shared step1-data-foundation step2-news step3-debate-decision \
  step4-alpha-hunter step5-portfolio-tracking step8-fundamental step9-technical \
  step10-macro; do
  (cd $step && uv pip install -e .)
done

# Start dashboard
cd step6-dashboard && npm run dev          # → localhost:5173

# Start backend
cd step7-automation && uvicorn axe_orchestrator.api:app --reload --port 8000

# Or use the launcher script
./scripts/axe-dev.sh                       # starts both API + Dashboard and reports data-source readiness
```

### CLI Entry Points

```bash
axe run all          # Full pipeline
axe run alpha        # Alpha scanner only
axe run news         # News ingestion only
axe run portfolio    # Portfolio review only
axe run specialists  # Fundamental + Technical + Macro
axe run specialists_decide # Specialists + decision pipeline
axe-fundamental      # Direct: fundamental analyst
axe-technical        # Direct: technical analyst
axe-macro            # Direct: macro strategist
```

---

## Project Status (April 2026)

| Area | Progress | Notes |
|------|----------|-------|
| Core infrastructure | ~80% | Retention policy and live verification remain |
| Dashboard UI | ~85% | Mobile optimization, search/filters pending |
| Agent pipeline (basic) | ~80% | Committee hardening and production validation remain |
| Full agent org | ~60% | Risk Manager and Compliance/Audit still pending |
| Automation | ~30% | Cron scheduling and Telegram alerts not yet built |

### Recent Milestones

- ✅ **Visible Prototype** (April 11) — Dashboard opens locally and renders the first artifact-driven panels
- ✅ **IBKR Flex Query Integration** (April 20) — Live portfolio data via Flex API with fallback
- ✅ **Portfolio sync fixes** — Dual-write for weekly review, SPY comparison formatting, P&L display
- ✅ **Specialist agents** — Fundamental, Technical, and Macro analyst agents built
- ✅ **Committee Room** (April 21) — Live ticker run, SSE event stream, CEO decision + playbook UI
- ✅ **Shared LLM helper** (April 21) — Centralized JSON call path for specialist agents

### Next Priorities

1. **Risk Manager agent** — Risk limits, drawdown monitoring, position-level veto power
2. **Compliance/Audit agent** — Source verification, assumption logging, audit trail
3. **Committee hardening** — More orchestration coverage, retention policy, cleaner artifact handling
4. **Production automation** — Cron during market hours, Telegram alerts, monthly PDF reports

---

## Key Files

| File | Purpose |
|------|---------|
| `ROADMAP.md` | Project milestones and gap analysis |
| `INVESTOR_PROFILE.md` | Operator's financial profile and decision rules |
| `AGENTS.md` | Agent ground rules and package structure |
| `CLAUDE.md` | Project context for AI assistants |
| `spec/` | Design specs (vision, strategy, architecture, org chart) |
| `plans/` | Implementation plans for specific features |
| `runbooks/` | Operational runbooks |
| `step6-dashboard/public/` | Live artifact contract consumed by the UI |
| `scripts/axe-dev.sh` | Development launcher (port-aware, color-coded) |

---

*Last updated: 2026-04-21*
