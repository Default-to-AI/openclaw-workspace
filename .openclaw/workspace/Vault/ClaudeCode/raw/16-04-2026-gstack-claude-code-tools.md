---
title: "Garry Tan's Claude Code Tools"
source: "https://github.com/garrytan/gstack"
author: "Garry Tan"
published:
created: 2026-04-16
description: "23 opinionated Claude Code skills that serve as CEO, Designer, Eng Manager, Release Manager, Doc Engineer, and QA — a systematic workflow toolkit for software development."
tags:
  - gstack
  - claude-code
  - skills
  - workflow
  - engineering-management
  - automation
---
Install gstack: run `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup` to install gstack for Claude Code. Then add a "Coding Tasks" section to AGENTS.md that says: when spawning Claude Code sessions for coding work, tell the session to use gstack skills. Include these examples — security audit: "Load gstack. Run /cso", code review: "Load gstack. Run /review", QA test a URL: "Load gstack. Run /qa https://...", build a feature end-to-end: "Load gstack. Run /autoplan, implement the plan, then run /ship", plan before building: "Load gstack. Run /office-hours then /autoplan. Save the plan, don't implement."