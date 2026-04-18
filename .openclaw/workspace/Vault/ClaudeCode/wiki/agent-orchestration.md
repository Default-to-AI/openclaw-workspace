---
title: Agent Orchestration
type: concept
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[OpenClaw/raw/2026-04-11-i-run-20-openclaw-agents-24-7-here-s-how-to-set-up-agent-teams]]"
  - "[[How I Use Obsidian + Claude Code to Run My Life]]"
tags:
  - agents
  - orchestration
  - multi-agent
  - patterns
  - coordination
---

# Agent Orchestration

Multi-agent coordination patterns for making AI agents work together rather than in isolation. Evidence drawn from [[openclaw]] fleets, [[axe-capital-architecture-summary|Axe Capital]], and personal OS workflows.

## Core Pattern: Orchestrator + Specialists

One orchestrator agent routes tasks to specialist agents. Each specialist has a defined role, tools, and output location. The orchestrator manages sequencing, dependencies, and conflict resolution.

```
         Orchestrator
        /     |      \
  Research  Content   Dev
    agent    agent   agent
        \     |      /
      Shared Workspace
```

**Why this matters:** Without an orchestrator, agents overlap on tasks, produce conflicting outputs, and burn through API credits. Build the orchestrator before adding more than 3 agents.

## Patterns Observed Across Sources

### 1. Independent Analysis Streams + Single Decision-Maker
From [[axe-capital-architecture-summary|Axe Capital]]: Multiple analysts (fundamental, technical, macro) produce independent reports. A CEO agent synthesizes into final recommendations. This prevents groupthink and ensures diverse analysis.

### 2. Dedicated Risk/Veto Agent
A risk agent with veto power sits between analysis and execution. Applicable to trading (risk manager), security (audit agent), and content (fact-checker). The veto is a hard gate, not a suggestion.

### 3. Devil's Advocate / Contrarian
From [[openclaw-agents-setup|Moe Lueker's fleet]]: Dedicated contrarian agents that challenge other agents' outputs. Forces better reasoning and surfaces blind spots.

### 4. Per-Agent Output Folders
Each agent writes to a dedicated directory in a shared workspace. Prevents file conflicts and makes it easy to trace which agent produced what. Example: `Reports/<agent-name>/YYYY-MM-DD.md`.

### 5. Approval Gates (Progressive Trust)
Paper/simulation mode is automatic. Live/production mode requires human approval. Trust is extended incrementally as the system proves reliability. From both [[claude-tradingview-trading|TradingView trading]] and [[axe-capital-architecture-summary|Axe Capital]].

### 6. Heartbeat Discipline
From [[openclaw-guides-summary|OpenClaw efficiency playbook]]: Heartbeats should only triage (check messages, check 1-2 conditions). If work is found, create a task and stop. Never run research pipelines in a heartbeat.

## Configuration Best Practices

| Config File | Purpose | Size Constraint |
|---|---|---|
| `soul.md` | Identity, personality, behavioral rules | <500 words (read every prompt) |
| `agents.md` | Tools, cron schedule, output location | As needed |
| `USER.md` | Human identity context | <1KB |

These two files determine 80% of agent usefulness. Longer soul.md = more tokens burned per interaction + more diluted rules.

## Scaling Guidelines

1. Start with 3 agents: orchestrator + 2 specialists. Get reliable first.
2. Add agents only when you have a clear, recurring job for them.
3. Each new agent needs its own soul.md, agents.md, output folder, and cron schedule.
4. Use cheap models for routine tasks; expensive models only for complex reasoning.
5. Rate outputs and give feedback; agents improve over time with training.

## See also

- [[openclaw]]
- [[openclaw-agents-setup]]
- [[axe-capital-architecture-summary]]
- [[security-hardening-ai-agents]]
- [[claude-code-obsidian-workflow]]
