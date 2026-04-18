---
title: "Claude Routines: Automation Platform"
type: source-summary
domain: claudecode
created: 15-04-2026
updated: 15-04-2026
sources:
  - "[[ClaudeCode/raw/15-04-2026-claude-routines-automation]]"
tags:
  - claude-code
  - routines
  - automation
  - api
  - workflows
---

# Claude Routines: Full Automation Platform

**Platform:** YouTube | **Author:** Nick Saraev | **Published:** 14-04-2026 | **Duration:** ~17 min

Anthropic's new **Routines** feature transforms Claude Code into a full automation platform — competing with no-code tools like n8n and Make.com.

## What are Routines?

Routines allow Claude to run automations on:
- **Schedule** — daily, hourly, etc.
- **Webhook** — triggered by external HTTP requests
- **API call** — programmatic execution

## Key Demos

### 1. Gmail Triage
- Claude checks Gmail via connector
- Summarizes unread emails
- Drafts polite decline/acceptance responses
- Sends summary to Slack

### 2. Transcript to Proposal
- Fireflies (transcript service) sends call data via API
- Routine triggers a managed agent
- Generates full business proposal automatically

### 3. n8n to Routines
- Copy n8n workflow JSON
- Ask Claude to convert to routine
- Natural language replaces drag-and-drop nodes

## Use Cases

- Replace proposal generators
- Post-call email + workflow diagram generation
- Client onboarding automation
- Any non-human-touch business workflow

## Connectors

Currently available:
- Gmail
- Slack
- (More coming)

## See also

- [[claude-code]]
- [[claude-code-obsidian-workflow]]
- [[agent-orchestration]]