---
title: Claude Code
type: entity
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[How I Use Obsidian + Claude Code to Run My Life]]"
  - "[[Claude Code + NotebookLM + Obsidian = GOD MODE]]"
tags:
  - claude-code
  - anthropic
  - cli
  - agent
  - tool
---

# Claude Code

Anthropic's official CLI agent. Runs in the terminal, has access to the filesystem, can execute code, read and write files, call external APIs, and spawn sub-agents. Unlike chat-based LLMs, Claude Code operates on persistent context — it reads files before responding and writes outputs back to disk.

## What makes it different from a chatbot

- **File system access:** reads and modifies files directly; no copy-paste loop
- **Tool use:** shell commands, web requests, code execution, MCP servers
- **Persistent context via CLAUDE.md:** loaded at session start, carries identity and rules across all conversations
- **Skills system:** reusable slash commands that encode workflows — composable and chainable
- **Sub-agents:** can spawn parallel agents for independent tasks

## The CLAUDE.md system

The most important configuration surface. Loaded before every session. Acts as the agent's operating manual: who the user is, how the vault is structured, what conventions to follow. Multiple CLAUDE.md files can exist (vault root, per-domain, per-project) and are all read on startup.

## Skills

Reusable slash commands defined as markdown files in `~/.claude/skills/`. Can be created manually or generated via the skill creator. A skill is a prompt template — Claude Code executes it when invoked. Skills can call other skills, making complex workflows composable into a single command.

## Role in this vault

Claude Code is the agent that maintains this wiki. It reads raw sources, writes wiki pages, updates the index, appends to the log, and answers queries by reading compiled wiki pages. The vault is its persistent workspace; CLAUDE.md is its operating brief.

## See also

- [[llm-wiki-pattern]]
- [[claude-code-obsidian-workflow]]
- [[notebooklm-integration]]
- [[agent-orchestration]]
- [[obsidian]]
