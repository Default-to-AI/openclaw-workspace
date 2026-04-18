---
title: Garry Tan's Claude Code Tools (gstack)
type: source-summary
domain: claudecode
created: 16-04-2026
updated: 16-04-2026
sources:
  - "[[16-04-2026-gstack-claude-code-tools]]"
tags:
  - gstack
  - claude-code
  - skills
  - workflow
---

# Garry Tan's Claude Code Tools (gstack)

Garry Tan's `gstack` is a collection of 23 opinionated Claude Code skills that serve as CEO, Designer, Engineering Manager, Release Manager, Doc Engineer, and QA — essentially replacing multiple specialist roles with a systematic workflow toolkit.

## What it provides

| Role | Capability |
|------|------------|
| CEO | Strategic oversight, prioritization |
| Designer | UI/UX thinking, visual feedback |
| Engineering Manager | Sprint planning, code review, team coordination |
| Release Manager | Deployment, shipping, rollback procedures |
| Doc Engineer | Documentation generation, API docs |
| QA | Testing, bug hunting, quality assurance |

## Installation and setup

1. Clone the repo:
   ```
   git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
   cd ~/.claude/skills/gstack
   ./setup
   ```

2. Add a "Coding Tasks" section to AGENTS.md that instructs sessions to use gstack skills.

## Usage examples

- Security audit: `Load gstack. Run /cso`
- Code review: `Load gstack. Run /review`
- QA test a URL: `Load gstack. Run /qa https://...`
- Build a feature end-to-end: `Load gstack. Run /autoplan, implement the plan, then run /ship`
- Plan before building: `Load gstack. Run /office-hours then /autoplan. Save the plan, don't implement.`

## See also

- [[claude-code]] — Claude Code entity page
- [[claude-code-obsidian-workflow]] — Core operating pattern
- [[agent-orchestration]] — Multi-agent coordination patterns