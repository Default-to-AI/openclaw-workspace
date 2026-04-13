---
title: "Summary: Axe Capital Agent Architecture"
type: source-summary
domain: finance
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[Archive/_old_50_AISphere/Projects/AxeCapital/01_Spec/02-system-architecture]]"
  - "[[Archive/_old_50_AISphere/Projects/AxeCapital/01_Spec/Org/org-chart-and-contracts]]"
tags: [axe-capital, agents, orchestration, trading, multi-agent]
---

# Summary: Axe Capital Agent Architecture

Axe Capital is a hedge-fund-style multi-agent system for investment research and (paper) trading. Extracted here for reusable [[agent-orchestration]] patterns.

## Agent Roles (Hedge Fund Org Chart)

| Role | Function | Constraints |
|---|---|---|
| CEO | Final decision-maker: 0-3 actions with rationale, sizing, invalidation, targets | Cannot fetch raw data (delegates) |
| COO/CFO | Process management, capital allocation, exposure/liquidity checks | |
| Portfolio Manager | Portfolio construction: concentration, diversification, factor tilts | |
| Risk Manager | Risk limits, max drawdown, scenario checks, correlation, position limits | Can veto |
| Fundamental Analyst | Business quality, earnings, balance sheet, valuation, thesis | |
| Technical Analyst | Market structure, entry/exit levels, trend confirmation, invalidation | |
| Macro Strategist | Rates, USD, liquidity, sector rotation, regime identification | |
| Compliance/Audit | Sources, assumptions, constraints checks, audit trail | |

## Reusable Patterns

1. **Independent analysis streams converging on a decision-maker.** Multiple specialist agents produce independent reports; one agent synthesizes into a final recommendation. Prevents groupthink.
2. **Explicit risk wrapper.** A dedicated risk agent with veto power sits between analysis and execution. See [[security-hardening-ai-agents]] for a parallel in security.
3. **Written investment memos as artifacts.** Every decision produces a structured document with sources, assumptions, constraints, and rationale. Applicable to any domain requiring auditable decisions.
4. **Approval gates.** Paper trading is automatic; live trading requires manual human approval. Progressive trust model.
5. **Per-agent output folders.** Each agent writes to its own directory (`Reports/<agent-name>/YYYY-MM-DD.md`). CEO output goes to approval queue + decision log.
6. **Reporting cadence.** Weekly full review + 1-3 proposals; daily risk monitor + thesis-break alerts.

## See also

- [[agent-orchestration]]
- [[algorithmic-trading-with-llms]]
- [[openclaw]]
- [[security-hardening-ai-agents]]
