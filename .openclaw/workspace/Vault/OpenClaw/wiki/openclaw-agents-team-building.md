---
title: "Source Summary: OpenClaw Agents — What They Are, What They Can Do, and How to Build a Team"
type: source-summary
domain: openclaw
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[OpenClaw/raw/15-04-2026-openclaw-agents-what-they-are]]"
tags: [openclaw, agents, team-building, orchestration, use-cases]
---

# Source Summary: OpenClaw Agents — Team Building Guide

**Platform:** Notion (gptprompts) | **Created:** 11-04-2026 | **Format:** Comprehensive guide

The definitive intro to OpenClaw for new users. Covers what an agent actually is, real-world use cases, and how to build a coordinated multi-agent fleet from scratch.

## The core distinction: agent vs. chatbot

A chatbot answers your question. An OpenClaw agent has a goal, tools to accomplish it, and a schedule — it runs without you.

OpenClaw agents can:
- **Remember everything** — conversations, preferences, context stored in local markdown files that persist for weeks/months
- **Act proactively** — wake up on schedules, check things, message you
- **Do real things** — browse, manage files, run code, execute shell commands
- **Talk to you anywhere** — Telegram, WhatsApp, Discord, Slack, Signal, iMessage

## Agent configuration: the two-file model

Every agent needs exactly two files:
- **`soul.md`** — identity, personality, behavioral rules. Keep under 500 words (read on every prompt; length = token cost = diluted rules)
- **`agents.md`** — tools, cron schedule, output location, startup instructions

These two files determine 80% of how useful the agent becomes.

## Agent fleet topology

The guide outlines role-based team structures:

| Role | Function |
|---|---|
| Orchestrator | Routes tasks, resolves conflicts, manages dependencies |
| Research agent | Scans trends, finds information, reports findings |
| Content agent | Drafts long-form content, social posts, scripts |
| Dev agent | Builds tools autonomously; give it a niche and check back in 2 days |
| Sales/outreach agent | Pipeline management, follow-ups |
| Feedback/QA agent | Reviews outputs from other agents |
| Devil's advocate | Challenges assumptions, prevents groupthink |

**Build the orchestrator before adding more than 3 agents.** Without coordination, agents overlap on tasks and burn credits.

## Use case categories

- Content creation: social media, YouTube scripts, newsletters
- Research: trend scanning, competitor monitoring, market research
- Personal productivity: daily briefings, task management, calendar management
- Development: overnight app building, automated testing
- Business ops: outreach, CRM updates, invoice processing

## Key principle: soul.md discipline

Keep soul.md under 500 words. Agents read it on every single prompt — the longer it is, the more tokens it burns and the more diluted your rules become.

## See also

- [[openclaw]]
- [[openclaw-agents-setup]]
- [[agent-orchestration]]
- [[openclaw-setup-and-efficiency]]
