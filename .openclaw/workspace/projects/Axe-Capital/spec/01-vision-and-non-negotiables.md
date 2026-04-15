---
type: spec
project: axe-capital
status: draft
created: 2026-04-11
tags: [axe-capital, investing, ibkr, risk]
---

# Axe Capital — Vision & Non-Negotiables

## Vision
An autonomous, hedge-fund-style agent system that manages your US equities portfolio via Interactive Brokers, with auditability, strict risk control, and human approval gates where required.

## Non-negotiables
- **Capital preservation first**: no strategy is allowed to risk catastrophic loss.
- **No "mystery trades"**: every trade must have a machine-readable rationale + human-readable explanation.
- **Paper-first**: prove it in IBKR paper trading before any live execution.
- **Explicit approval gates**: live trading requires your approval until we explicitly downgrade gates.
- **Deterministic controls**: position sizing, max exposure, max drawdown, and kill-switches.
- **Full audit trail**: every decision gets logged (inputs, model output, rule checks, final action).

## What success looks like (phase 1)
- Daily/weekly research pipeline produces a short list of candidates with clear theses.
- A single "portfolio brain" proposes trades with sizing and risk checks.
- You approve trades from a clean queue.
- All actions are logged into Obsidian + a machine log (jsonl).
