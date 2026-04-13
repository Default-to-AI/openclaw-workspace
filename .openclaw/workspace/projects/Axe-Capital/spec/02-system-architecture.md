---
type: spec
project: axe-capital
status: draft
created: 2026-04-11
tags: [axe-capital, architecture, agents]
---

# System Architecture (Draft)

## Roles (agents)
- **Orchestrator**: routes work, owns the daily plan, produces the final "approval queue".
- **Research agent**: gathers sources, extracts facts, writes research notes.
- **Modeling agent**: turns research into a thesis + valuation / scenario sketch.
- **Risk agent**: enforces risk limits and produces pass/fail + sizing.
- **Execution agent**: prepares orders, validates constraints, and (paper) submits to IBKR.
- **Audit agent**: writes the decision log and sanity-checks inconsistencies.

## Artifacts
- Obsidian notes: theses, research, decision log.
- Machine logs: jsonl of every step.
- Approval queue: a single markdown note + optional CSV of proposed orders.

## Approval gates
- Paper trading can be automatic.
- Live trading remains manual approval until we explicitly change this.
