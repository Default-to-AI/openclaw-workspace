---
title: Algorithmic Trading with LLMs
type: concept
domain: finance
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[Claude Can Now TRADE For You On TradingView (Insane)]]"
  - "[[projects/Axe-Capital/spec/02-system-architecture]]"
  - "[[projects/Axe-Capital/spec/Org/org-chart-and-contracts]]"
tags:
  - trading
  - llm
  - automation
  - tradingview
  - crypto
  - agents
---

# Algorithmic Trading with LLMs

Using LLMs as the decision layer between market data sources and trade execution, from simple single-agent bots to multi-agent hedge fund simulations.

## Two Architectures Observed

### 1. Single-Agent Trading Bot (Lewis Jackson)

```
TradingView --> Claude Code --> Exchange API
  (signals)    (safety filter)   (execution)
```

- Claude sits between chart and exchange; they never communicate directly.
- Strategy defined in `rules.json` with all conditions, indicators, Pine Script.
- Multi-condition safety filter: ALL conditions must pass or trade is blocked.
- Deployed on Railway (cloud, 24/7 cron job).
- Full trade logging for accounting/tax.
- Source: [[claude-tradingview-trading]]

### 2. Multi-Agent Hedge Fund (Axe Capital)

```
Fundamental Analyst  \
Technical Analyst     |-> CEO (decision) -> Approval Queue -> Human
Macro Strategist     /         |
Risk Manager (veto) -----------+
```

- Independent analysis streams converge on a single decision-maker.
- Risk agent has veto power.
- Written investment memos with sources, assumptions, constraints.
- Per-agent output folders + decision log.
- Source: [[axe-capital-architecture-summary]]

## Common Patterns

1. **Paper trading first.** Both architectures default to paper/simulation mode. Live trading requires explicit opt-in. This is non-negotiable for any new strategy.
2. **Strategy as structured data.** The trading strategy is stored as a structured file (rules.json or spec docs), not embedded in prompts. This makes it auditable, versionable, and separable from the agent logic.
3. **Every decision logged.** Both trades and non-trades are recorded with reasoning. Essential for:
   - Strategy debugging
   - Tax/accounting compliance
   - Audit trail
4. **Safety filters / risk gates.** A dedicated validation step between analysis and execution. In the simple bot: multi-condition check. In Axe Capital: a dedicated risk agent with veto.
5. **Human remains in the loop.** Even in the "automated" setup, the human approves (or at minimum reviews) live trades. Full automation is a future state earned through demonstrated reliability.

## Strategy Sourcing

From [[claude-tradingview-trading|Lewis Jackson]]: Use Apify to scrape YouTube channel transcripts of traders, then ask Claude to deduce and formalize their strategy into rules.json. A creative (if imperfect) way to bootstrap strategy development.

## Risks and Disclaimers

- Strategy quality determines outcome entirely. A bad strategy executed perfectly is still a bad strategy.
- LLM hallucination in a trading context can mean real financial loss.
- API key security is paramount when connected to exchanges holding real funds.
- Backtesting on historical data does not guarantee future performance.
- Tax implications vary by jurisdiction; automated logging helps but does not replace professional advice.

## Data Access Layer

For programmatic access to IBKR portfolio data (positions, cash balances, P&L, margin) as an input to any trading or monitoring system, see [[ibkr-tws-api-portfolio-data]]. The TWS API uses a subscribe-and-publish model — connect once, receive real-time streaming updates via callbacks.

Note: No historical position data is available via the API. For historical data, use IBKR Flex Queries.

## See also

- [[claude-tradingview-trading]]
- [[axe-capital-architecture-summary]]
- [[agent-orchestration]]
- [[security-hardening-ai-agents]]
- [[claude-code]]
- [[ibkr-tws-api-portfolio-data]]
- [[interactive-brokers]]
