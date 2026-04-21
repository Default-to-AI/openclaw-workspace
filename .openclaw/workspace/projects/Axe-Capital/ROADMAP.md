# Axe Capital — Project Roadmap

**Last Updated:** 2026-04-21
**Status:** In Progress

---

## 1. What Is Axe Capital?

Axe Capital is a **hedge-fund-style multi-agent research platform** that hunts for market-beating opportunities.

**NOT a dashboard app** — The dashboard is just the VIEW layer. The real system is the agent pipeline:
- Data ingestion (news, SEC filings, IBKR portfolio)
- Independent analysis by specialist agents
- Adversarial debate (bull vs bear)
- CEO decision and position playbook for Robert to execute manually at IBKR
- Full audit trail (traces)

**Core thesis:** Retail doesn't do exhaustive multi-source research. Axe Capital's edge is depth, speed, and adversarial structure.

---

## 2. Agent Org Chart

| Role | Function | Status |
|------|----------|--------|
| **CEO** | Final decision-maker: actions with rationale, sizing, invalidation | step3 + committee flow |
| **COO/CFO** | Process management, capital allocation, exposure checks | step1 (axe-coo) |
| **Portfolio Manager** | Portfolio construction, concentration, diversification | step5 (axe-portfolio) |
| **Risk Manager** | Risk limits, drawdown, correlation, position limits. Can veto. | Partial via CRO gate |
| **Fundamental Analyst** | Business quality, earnings, balance sheet, valuation | step8 built |
| **Technical Analyst** | Market structure, entry/exit levels, trend confirmation | step9 built |
| **Macro Strategist** | Rates, USD, liquidity, sector rotation, regime | step10 built |
| **Compliance/Audit** | Sources, assumptions, audit trail | Not built |

**Current implementation:**
- step0 (axe_core) — Shared utilities ✓
- step1 (axe_coo) — COO data pipeline ✓
- step2 (axe_news) — RSS ingestion + LLM scorer ✓
- step3 (axe_decision) — Debate layer (basic) ✓
- step4 (axe_alpha) — Alpha scanning ✓
- step5 (axe_portfolio) — Portfolio tracker ✓
- step6 (dashboard) — React UI with overview/research/ops/committee flows ✓
- step7 (axe_orchestrator) — CLI + FastAPI + SSE committee backend ✓
- step8 (axe_fundamental) — Fundamental analyst ✓
- step9 (axe_technical) — Technical analyst ✓
- step10 (axe_macro) — Macro strategist ✓

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
- [x] FastAPI backend with refresh buttons
- [x] SSE for trace streaming
- [x] Portfolio source fallback (`IBKR -> Flex Query -> cached CSV`)
- [x] Dashboard source labeling for portfolio freshness
- [ ] End-to-end `run all` verification against live environment

### Milestone C — Full Agent Org (IN PROGRESS)
- [x] CEO agent implementation
- [ ] Risk Manager agent implementation
- [x] Fundamental Analyst agent implementation
- [x] Technical Analyst agent implementation
- [x] Macro Strategist agent implementation
- [ ] Compliance/Audit agent implementation
- [x] Full debate pipeline (bull vs bear -> CRO -> CEO)
- [x] Live committee room event stream
- [x] Position playbook generation
- [ ] Tight specialist -> debate wiring validation in production

### Milestone D — Production Ready
- [ ] Cron / market-hours automation
- [ ] Telegram alerts
- [ ] Monthly PDF reports
- [ ] Full audit trail review

---

## 4. Data Pipeline

```
[RSS feeds]      [SEC EDGAR, yfinance]     [IBKR live / Flex / CSV]
     │                   │                         │
     ▼                   ▼                         ▼
  axe_news      axe_alpha                 axe_portfolio
                                                    │
                              ┌─────────────────────┴─────────────────────┐
                              ▼                                           ▼
                   specialist agents (fundamental / technical / macro)   weekly review
                              │
                              ▼
                    bull -> bear -> CRO -> CEO -> playbook
                              │
                              ▼
                     step6-dashboard/public/ artifacts
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
            React dashboard          FastAPI + SSE
```

---

## 5. Key Files

| File | Description |
|------|-------------|
| `spec/15-04-2026-research-platform-design.md` | Full design spec |
| `spec/Org/org-chart-and-contracts.md` | Agent roles and contracts |
| `AGENTS.md` | Agent ground rules (this repo) |
| `CLAUDE.md` | Project context |
| `docs/description-axe-capital.md` | Current project description |

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
axe run specialists_decide # Run specialists + decision
axe run all      # Run all pipelines
```

---

## 7. Issues & Tech Debt (UPDATED 2026-04-21)

### Completed
- [x] Fix spec file naming (renamed 00→01, 01→02, 02→03)
- [x] Delete `axe-capital-dashboard-mockup.html`
- [x] Delete `axe-capital.md` (duplicate spec)
- [x] Move legacy `dashboard/` → `deprecated/legacy-dashboard/`

### High Priority
- [ ] Prune old traces / artifacts with an explicit retention policy
- [ ] Add tests around committee orchestration beyond helper/unit coverage
- [ ] Remove generated `__pycache__` / artifact noise from future diffs
- [ ] Replace deleted legacy startup scripts with one documented blessed flow

---

## 8. What's Left (Summary)

| Category | Done | Left |
|----------|------|------|
| Core infrastructure | 80% | Retention policy, verification, cleanup |
| UI/Dashboard | 85% | Mobile polish, search, filters |
| Agent pipeline (simple) | 80% | Live validation and hardening |
| Agent org (full) | 60% | Risk + Compliance/Audit remain |
| Automation | 30% | Cron, Telegram |
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
| **Fundamental Analyst** | Business quality, earnings, valuation | ✓ (step8) |
| **Technical Analyst** | Market structure, entry/exit levels | ✓ (step9) |
| **Macro Strategist** | Rates, USD, liquidity, regime | ✓ (step10) |
| **Compliance/Audit** | Sources, audit trail | ❌ NOT built |

### Current Flow
```
ticker
  → portfolio/news/yfinance context
  → Fundamental / Technical / Macro specialists
  → Bull + Bear
  → CRO
  → CEO
  → position playbook
```

### What's Missing
1. **Risk + Compliance roles**
   - Risk manager with explicit veto/risk budgeting
   - Compliance/audit pass over evidence quality
2. **Production hardening**
   - Better orchestration tests
   - Artifact retention / pruning
   - Live-env verification
3. **Operator automation**
   - Scheduled refresh
   - Telegram alerts
   - Monthly reporting

---

## 10. Next Priority

The gap between spec and implementation is now:
- Risk Manager is still only partial
- Compliance/Audit is still missing
- The committee pipeline exists, but needs production hardening and automation

**Recommended next build:** Implement Risk Manager and Compliance/Audit as first-class agents, then harden the committee pipeline for scheduled operation.

---

*Last updated: 2026-04-21*
