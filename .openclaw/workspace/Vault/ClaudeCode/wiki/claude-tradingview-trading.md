---
title: "Source Summary: Claude Can Now TRADE For You On TradingView (Insane)"
type: source-summary
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[ClaudeCode/raw/15-04-2026-claude-code-tradingview.md]]"
tags:
  - tradingview
  - trading
  - mcp
  - claude-code
  - automation
  - crypto
---

# Source Summary: Claude Can Now TRADE For You On TradingView (Insane)

**Author:** Lewis Jackson | **Published:** 08-04-2026 | **Format:** YouTube video

Continuation of a prior setup video. This one closes the loop: Claude Code reads live TradingView signals, applies a multi-condition safety filter, and executes real trades on a crypto exchange — all running 24/7 on Railway (cloud).

## Core thesis

A fully automated trading loop is achievable with no coding experience. The architecture is deliberately simple: three tools, each doing one job. The complexity lives in the safety filter and strategy rules, not the plumbing.

## Architecture

```
TradingView (data + signals)
       ↓
  Claude Code (decision layer + safety filter)
       ↓
  Crypto exchange (execution via API keys)
       ↓
  Spreadsheet log (accounting/tax records)
```

- **TradingView** — provides price data, indicators, Pine Script strategy signals
- **Claude Code** — reads signals, checks multi-condition safety filter, decides whether to execute
- **Exchange (e.g. Bitget)** — receives trade orders via API keys
- **Railway** — hosts the whole system in the cloud, runs 24/7 without a laptop

## Key implementation details

### One-shot prompt
The entire setup is in a single prompt from GitHub. Pasted into Claude Code, it spawns an onboarding agent that opens files, opens websites, and walks through every step. Setup time: ~5 minutes.

### Safety filter
Claude applies a multi-condition filter before executing any trade. The strategy rules live in a `rules.json` file — Claude checks all conditions are met before placing an order. If blocked, it logs the reason. This is the approval gate pattern from [[agent-orchestration]].

### Paper trading first
System defaults to paper trading mode on setup. All signals and decisions are logged but no real money moves. Human switches to live mode explicitly when ready. Implements the progressive trust pattern.

### Accounting log
Every trade (executed or blocked) is logged to a spreadsheet in accountant-friendly format. Tax records are a first-class output, not an afterthought.

### Bonus: transcript scraping
Lewis demos scraping YouTube transcripts via the Amplify API to extract trading strategies from other traders and feed them into the `rules.json`. A practical way to source strategy ideas.

## Limitations of this source

Crypto-focused (uses Bitget). Applies to equities in principle but exchange integration would differ. The safety filter is only as good as the strategy rules — garbage in, garbage out. Running with real money requires serious testing. Lewis explicitly disclaims financial advice.

## See also

- [[tradingview]]
- [[agent-orchestration]]
- [[claude-code]]
- [[algorithmic-trading-with-llms]]
