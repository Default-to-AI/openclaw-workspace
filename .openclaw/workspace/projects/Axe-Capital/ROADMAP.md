# Axe Capital — Project Roadmap

**Last Updated:** 2026-04-15
**Status:** In Progress

---

## 1. What Is Axe Capital?

Axe Capital is a **hedge-fund-style multi-agent research platform** that hunts for market-beating opportunities.

**NOT a dashboard app** — The dashboard is just the VIEW layer. The real system is the agent pipeline:
- Data ingestion (news, SEC filings, IBKR portfolio)
- Independent analysis by specialist agents
- Adversarial debate (bull vs bear)
- Decision memo for Robert to execute manually at IBKR
- Full audit trail (traces)

**Core thesis:** Retail doesn't do exhaustive multi-source research. Axe Capital's edge is depth, speed, and adversarial structure.

---

## 2. Agent Org Chart

| Role | Function | Status |
|------|----------|--------|
| **CEO** | Final decision-maker: actions with rationale, sizing, invalidation | Not built |
| **COO/CFO** | Process management, capital allocation, exposure checks | step1 (axe-coo) |
| **Portfolio Manager** | Portfolio construction, concentration, diversification | step5 (axe-portfolio) |
| **Risk Manager** | Risk limits, drawdown, correlation, position limits. Can veto. | Not built |
| **Fundamental Analyst** | Business quality, earnings, balance sheet, valuation | Not built |
| **Technical Analyst** | Market structure, entry/exit levels, trend confirmation | Not built |
| **Macro Strategist** | Rates, USD, liquidity, sector rotation, regime | Not built |
| **Compliance/Audit** | Sources, assumptions, audit trail | Not built |

**Current implementation:**
- step0 (axe_core) — Shared utilities ✓
- step1 (axe_coo) — COO data pipeline ✓
- step2 (axe_news) — RSS ingestion + LLM scorer ✓
- step3 (axe_decision) — Debate layer (basic) ✓
- step4 (axe_alpha) — Alpha scanning ✓
- step5 (axe_portfolio) — Portfolio tracker ✓
- step6 (dashboard) — React UI (7 panels) ✓
- step7 (axe_orchestrator) — CLI + FastAPI ✓

---

## 3. Milestones

### Milestone A — Visible Prototype (COMPLETED 2026-04-11)
- [x] Dashboard opens locally
- [x] 7 panels render artifact data
- [x] Basic layout

### Milestone B — Functional Platform (IN PROGRESS)
- [x] `axe_core` + trace lib
- [x] Wire trace into agents
- [x] `axe_news` RSS + LLM scorer
- [x] Alpha panel reading `alpha-latest.json`
- [x] News panel reading `news-latest.json`
- [x] Agent Status Board from `health.json`
- [x] Trace viewer reading `traces/<run-id>.json`
- [x] Decision Archive from `decision-log.jsonl`
- [ ] FastAPI backend with refresh buttons
- [ ] SSE for real-time trace streaming
- [ ] End-to-end `run all` verification

### Milestone C — Full Agent Org (NEXT PRIORITY)
- [ ] CEO agent implementation
- [ ] Risk Manager agent implementation
- [ ] Fundamental Analyst agent implementation
- [ ] Technical Analyst agent implementation
- [ ] Macro Strategist agent implementation
- [ ] Compliance/Audit agent implementation
- [ ] Full debate pipeline (bull vs bear)
- [ ] Investment memo generation

### Milestone D — Production Ready
- [ ] Cron automation
- [ ] Telegram alerts
- [ ] Monthly PDF reports
- [ ] Full audit trail review

---

## 4. Data Pipeline

```
[RSS feeds]      [SEC EDGAR, yfinance]     [IBKR CSV]
     │                   │                     │
     ▼                   ▼                     ▼
  axe_news      axe_alpha             axe_portfolio
     │                   │                     │
     └───────────────────┴─────────────────────┘
                    all trace
                      │
                      ▼
              ./public/ (artifacts)
                  │
                  ▼
            React dashboard
                  │
                  ▼
            FastAPI (optional)
```

---

## 5. Key Files

| File | Description |
|------|-------------|
| `spec/15-04-2026-research-platform-design.md` | Full design spec (approved) |
| `spec/Org/org-chart-and-contracts.md` | Agent roles and contracts |
| `AGENTS.md` | Agent ground rules (this repo) |
| `CLAUDE.md` | Project context |
| `step6-dashboard/README.md` | Dashboard docs |

---

## 6. Commands Reference

```bash
# Development
cd step6-dashboard && npm run dev     # Dashboard on :5173

# Backend
cd step7-automation
uv pip install -e ".[api]"
uvicorn axe_orchestrator.api:app --reload --port 8000

# Agent pipelines
axe run alpha     # Run alpha hunter
axe run news     # Run news ingestion
axe run portfolio # Run portfolio review
axe run all      # Run all pipelines
```

---

## 7. Issues & Tech Debt (UPDATED 2026-04-15)

### Completed
- [x] Fix spec file naming (renamed 00→01, 01→02, 02→03)
- [x] Delete `axe-capital-dashboard-mockup.html`
- [x] Delete `axe-capital.md` (duplicate spec)
- [x] Move legacy `dashboard/` → `deprecated/legacy-dashboard/`

### High Priority
- [ ] Prune old traces (keep last 10)

---

## 8. What's Left (Summary)

| Category | Done | Left |
|----------|------|------|
| Core infrastructure | 70% | Trace pruning, FastAPI |
| UI/Dashboard | 80% | Mobile, search, filters |
| Agent pipeline (simple) | 60% | Full debate, memo gen |
| Agent org (full) | 10% | 6 of 8 agents |
| Automation | 20% | Cron, Telegram |
| Production | 0% | Everything else |

---

## 9. Gap Analysis: Spec vs Implementation

### What Spec Requires (per org-chart-and-contracts.md)
| Agent Role | Purpose | Implemented? |
|------------|---------|--------------|
| **CEO** | Final decision-maker | ✓ (step3: CRO → CEO flow) |
| **COO/CFO** | Operations, capital allocation | ✓ (step1: axe-coo) |
| **Portfolio Manager** | Portfolio construction | ✓ (step5: axe-portfolio) |
| **Risk Manager** | Risk limits, can veto | ⚠️ Partially (CRO in step3) |
| **Fundamental Analyst** | Business quality, earnings, valuation | ❌ NOT built |
| **Technical Analyst** | Market structure, entry/exit levels | ❌ NOT built |
| **Macro Strategist** | Rates, USD, liquidity, regime | ❌ NOT built |
| **Compliance/Audit** | Sources, audit trail | ❌ NOT built |

### Current Flow (step3-debate-decision)
```
ticker → Bull + Bear → CRO → CEO → decision memo
```
**Missing:** Specialist analyst reports SHOULD feed into Bull/Bear first:
```
ticker → [Fundamental Analyst] → [Technical Analyst] → [Macro Strategist]
                              ↓
                          Bull + Bear (with analyst inputs)
                              ↓
                            CRO → CEO
```

### What's Missing
1. **Specialist Agents** (run first, produce reports):
   - Fundamental Analyst agent
   - Technical Analyst agent  
   - Macro Strategist agent
2. **Pipeline Orchestration** — These agents must run in sequence, feed into debate
3. **Output Contracts** — Each agent should write to `Reports/<agent-name>/YYYY-MM-DD.md`

---

## 10. Next Priority

The gap between spec and implementation is:
- **6 of 8 agents not built**
- No proper analyst → debate → decision pipeline

**Recommended next build:** Implement the 3 missing specialist agents (Fundamental, Technical, Macro) and wire them into the debate flow.

---

*Last updated: 2026-04-15*