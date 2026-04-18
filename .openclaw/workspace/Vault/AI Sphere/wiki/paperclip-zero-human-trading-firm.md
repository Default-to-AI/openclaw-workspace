---
title: PaperClip: zero-human trading firm walkthrough (source summary)
type: source-summary
domain: ai-sphere
created: 18-04-2026
updated: 18-04-2026
sources:
  - "[[AI Sphere/raw/18-04-2026-how-to-create-a-personal-zero-human-trading-firm]]"
tags:
  - agent-orchestration
  - ai-agents
  - trading-systems
---

## Summary
A YouTube interview with the anonymous founder of **PaperClip** (open-source agent orchestration framework) describing the shift from single-agent usage to **structured teams of agents** with roles, accountability, and an org chart (CEO/CTO + departments). The conversation frames an “AI trading firm” as an example: research agents generate ideas, backtest agents validate, risk agents constrain, and reporting agents keep a human “board” in control.

## Key ideas
- **Org chart as control surface**: agents are organized like employees with explicit roles, responsibilities, and reporting lines.
- **Bring-your-own harness**: plug in different runtimes (Claude Code, Codex, Gemini, OpenClaw, etc.) under one coordinating organization.
- **Accountability + taste injection**: the human guides direction and quality, rather than fully delegating blindly.
- **Trading-firm decomposition**: research → backtesting → risk layer → execution, coordinated by a top-level agent.

## Claims to verify / follow-ups
- PaperClip repo details (stars, install command, licensing) should be verified from the upstream source.

## See also
- [[AI Sphere/wiki/agent-orchestration]]
- [[OpenClaw/wiki/agent-orchestration]]
