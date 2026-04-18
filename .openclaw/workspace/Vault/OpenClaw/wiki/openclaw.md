---
title: OpenClaw
type: entity
domain: openclaw
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[OpenClaw/raw/2026-04-11-i-run-20-openclaw-agents-24-7-here-s-how-to-set-up-agent-teams]]"
  - "[[OpenClaw/raw/openclaw-first-15-messages-localized]]"
  - "[[OpenClaw/raw/openclaw-efficiency-playbook]]"
  - "[[OpenClaw/raw/secure-openclaw-wsl-windows]]"
  - "[[How I Use Obsidian + Claude Code to Run My Life]]"
  - "[[openclaw-release-changelogs-early-2026]]"
tags:
  - openclaw
  - agents
  - autonomous
  - platform
---

# OpenClaw

An autonomous AI agent platform that can run 24/7, execute scheduled tasks, coordinate multi-agent teams, and communicate via Telegram/WhatsApp. Distinct from [[claude-code]] in that it runs persistently and autonomously rather than interactively.

## Core Concepts

- **Agent vs Chatbot:** A chatbot answers questions. An OpenClaw agent has a goal, tools to accomplish it, and a schedule -- it runs without you.
- **Doer vs Director Identity:** Recommended by [[dan-martell-smart-with-ai|Dan Martell]] as a critical tool to automate the 92% of business tasks that are easy for computers but hard for humans, forcing you to focus on the 8% (taste, vision, care).
- **soul.md:** Defines agent identity, personality, and behavioral rules. Keep under 500 words (read on every prompt).
- **agents.md:** Defines startup instructions, tools, cron schedule, and output location.
- **Cron jobs:** Scheduled tasks that run at defined intervals (heartbeats, reports, content generation).
- **Channels:** Communication interfaces (Telegram, WhatsApp, web).
- **Skills:** Reusable capabilities that agents can invoke.
- **Shared workspace:** Common directory where agents read/write outputs.

## Deployment Options

| Platform | Notes |
|---|---|
| VPS (Hostinger) | Recommended. Isolated, 24/7, $6.49-13/mo. KVM2 (8GB RAM) or KVM4 (16GB RAM). |
| Windows + WSL | Possible but requires extra security hardening. See [[security-hardening-ai-agents]]. |
| Local machine | Not recommended due to security concerns (agent has filesystem access). |

## Integration with Obsidian

OpenClaw can read from and write to an Obsidian vault, enabling:
- Vault-aware scheduling and delegation
- Agent outputs as markdown notes in the vault
- Human reviews agent work via Obsidian UI

Vin (from [[obsidian-claude-code-run-my-life]]) describes using OpenClaw to make decisions based on vault context without prompting -- the vault *is* the instruction set.

## Key Operational Guides in This Vault

- [[openclaw-setup-and-efficiency]] -- Setup path, efficiency drivers, context discipline
- [[security-hardening-ai-agents]] -- Threat model and hardening checklist
- [[agent-orchestration]] -- Multi-agent coordination patterns

## See also

- [[openclaw-setup-and-efficiency]]
- [[agent-orchestration]]
- [[security-hardening-ai-agents]]
- [[claude-code]]
- [[openclaw-agents-setup]]
- [[openclaw-guides-summary]]
- [[openclaw-team]]
- [[openclaw-release-changelogs-early-2026]]
