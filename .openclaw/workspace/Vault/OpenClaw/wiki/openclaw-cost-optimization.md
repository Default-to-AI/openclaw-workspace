---
title: "Source Summary: OpenClaw Cost Optimization Guide — Cut API Bills by 70–97%"
type: source-summary
domain: openclaw
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[OpenClaw/raw/2026-04-11-openclaw-cost-optimization-guide-notion-link]]"
tags: [openclaw, cost, optimization, model-routing, openrouter, tokens]
---

# Source Summary: OpenClaw Cost Optimization Guide

**Platform:** Notion (gptprompts) | **Created:** 11-04-2026 | **Format:** Technical guide with pricing tables

The most quantitative OpenClaw guide available. Covers the six cost drivers with percentage impact estimates, a 2026 model pricing comparison table, and specific configuration steps to achieve 70–97% API cost reduction.

## The inescapable baseline: 136K tokens

Every single OpenClaw request carries ~136K tokens of base overhead — system prompt + tool schemas. This is unavoidable. Every optimization works *around* this floor, not below it. Understanding this changes how you think about cost: minimize waste *per request*, since the base is fixed.

## The 6 cost drivers (with impact estimates)

| Driver | % of Bill | Fix |
|---|---|---|
| Wrong default model | 40–70% | Route by task complexity, not one model for everything |
| Heartbeats hitting paid models | 15–30% | Heartbeats → cheapest model only |
| Bloated context windows | 20–50% | Index-first, minimal snippets, one objective per session |
| No prompt caching | 10–40% | Repeat queries → 90% discount with caching |
| Session bloat | 10–30% | Long sessions = accumulated context; reset on topic change |
| Verbose tool outputs | 5–20% | Write logs to files; only key lines in chat |

## 2026 model pricing table (via OpenRouter, as of 24-02-2026)

### Budget tier — use for 80%+ of tasks

| Model | Input | Output | Blended* |
|---|---|---|---|
| GPT-5 Nano | $0.05 | $0.40 | $0.14 |
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | $0.18 |
| DeepSeek V3.2 | $0.28 | $0.40 | $0.31 |
| GPT-5 Mini | $0.25 | $2.00 | $0.69 |
| Gemini 2.5 Flash | $0.30 | $2.50 | $0.85 |

*Blended = weighted at 3:1 input-to-output ratio

### Mid tier — quality when needed

| Model | Input | Output | Blended |
|---|---|---|---|
| Claude Haiku 4.5 | $1.00 | $5.00 | $2.00 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $6.00 |

### Premium tier — use sparingly

| Model | Input | Output | Blended |
|---|---|---|---|
| Claude Opus 4.6 | $5.00 | $25.00 | $10.00 |
| GPT-5 | $1.25 | $10.00 | $3.44 |

**Ratio implication:** Using Claude Opus 4.6 instead of Gemini 2.5 Flash-Lite costs ~55× more per token. For heartbeats running 48× per day, that's a meaningful daily difference.

## Recommended routing strategy

- **Heartbeats:** Cheapest budget model (Gemini Flash-Lite or GPT-5 Nano)
- **Routine tasks** (summarization, classification, simple generation): Budget tier
- **Architecture, complex reasoning, security-sensitive:** Mid or premium
- **Never:** Default all tasks to one model

## Prompt caching

If you're sending the same system prompt repeatedly (which OpenClaw does constantly), caching gives a 90% discount on those tokens. Enable it via OpenRouter's caching settings. High-impact, zero-effort optimization.

## See also

- [[openclaw]]
- [[openclaw-setup-and-efficiency]]
- [[openclaw-guides-summary]]
