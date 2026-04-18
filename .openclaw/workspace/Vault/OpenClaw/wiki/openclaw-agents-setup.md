---
title: "Summary: I Run 20 OpenClaw Agents 24/7 -- How to Set Up Agent Teams"
type: source-summary
domain: openclaw
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[OpenClaw/raw/2026-04-11-i-run-20-openclaw-agents-24-7-here-s-how-to-set-up-agent-teams]]"
tags: [openclaw, agents, orchestration, dashboard, vps]
---

# Summary: I Run 20 OpenClaw Agents 24/7 -- How to Set Up Agent Teams

Moe Lueker walks through his full [[openclaw]] agent fleet: 20 agents on a VPS for <$7/month, with a command center dashboard.

## Key Architecture Decisions

1. **Agent vs Chatbot distinction.** A chatbot answers questions. An agent has a goal, tools, and a schedule -- it runs without you.
2. **Two config files per agent:**
   - `soul.md` -- identity, personality, behavioral rules (keep under 500 words; read on every prompt)
   - `agents.md` -- startup instructions, tools, cron schedule, output location
   - These two files determine 80% of agent usefulness.
3. **Orchestrator pattern.** One orchestrator routes tasks to specialist agents. Without coordination, agents overlap and burn credits. See [[agent-orchestration]].
4. **Shared workspace with per-agent output folders.** Agents writing to the same location without structure creates conflicts.
5. **Devil's advocate agents.** Contrarian agents that challenge other agents' outputs to avoid groupthink.

## Agent Fleet Example

| Agent Type | Role |
|---|---|
| Orchestrator | Routes tasks, coordinates |
| Content agent | Drafts long-form content |
| Product agent | Builds digital products |
| Research agent | Trend scanning, fact-finding |
| Dev agent | Builds tools autonomously overnight |
| Sales agent | Outreach and pipeline |
| Devil's advocate | Challenges assumptions |
| Feedback agent | Quality review |

## Command Center Dashboard

- Fleet overview with per-agent status, cost, active tasks
- Pipeline view (backlog, in-progress, review, done)
- Approval system for human-in-the-loop gates
- Gallery for non-text outputs (thumbnails, images)
- File browser for markdown artifacts
- Reports view for agent-generated reports

## Cost Optimization

- Average daily cost ~25 cents per agent with heavy optimization
- Use [[openclaw]] on a VPS (Hostinger KVM2/KVM4, $6.49-13/mo) instead of local machine for security
- Use OpenRouter for single-key access to multiple models; assign different models per agent
- Cheap models for heartbeats, expensive models only for architecture/security tasks

## Practical Tips

- Build orchestrator before adding more than 3 agents
- Start with 3 agents (orchestrator + content + research), get reliable, then expand
- When agents hit errors, paste logs into ChatGPT/Gemini for debugging
- Rate agent outputs and give feedback; they adjust over time
- Cron jobs for scheduled tasks (40 cron jobs in Moe's setup)

## See also

- [[openclaw]]
- [[agent-orchestration]]
- [[security-hardening-ai-agents]]
- [[openclaw-setup-and-efficiency]]
