---
title: "Source Summary: How I Use Obsidian + Claude Code to Run My Life"
type: source-summary
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[ClaudeCode/raw/23-02-2026-obsidian-claude-code-run-my-life.md]]"
tags:
  - obsidian
  - claude-code
  - personal-os
  - slash-commands
  - thinking-tools
  - vault
---

# Source Summary: How I Use Obsidian + Claude Code to Run My Life

**Authors:** Greg Isenberg + Vin (Internet Vin) | **Published:** 23-02-2026 | **Format:** YouTube interview / live demo

The most technically detailed source on using Obsidian + Claude Code as a personal operating system. Vin demonstrates a fully operational vault with custom slash commands, showing Claude Code functioning as a thinking partner — not just a task executor.

## Core thesis

The more you write into your vault, the more capable your AI partner becomes. Writing and daily reflection are the engine. The vault is the fuel. Claude Code is the reasoning layer that transforms accumulated notes into insight, ideas, and action.

*"Markdown files are the oxygen of LLMs. If you are serious about building a personal OS with AI, a centralized markdown-based note-taking system is table stakes."*

## Key ideas

### Obsidian CLI: the bridge

The Obsidian CLI plugin exposes the vault's link graph — not just file contents, but the relationships between files — to Claude Code. This enables Claude to traverse connections and surface cross-domain patterns the human has been circling without realizing it.

Example: a note about filmmaking is linked to a note about worldbuilding. Claude sees that connection and can surface it in response to an unrelated query.

### Custom slash commands as thinking tools

Vin built a suite of skills that turn Claude Code into a personalized thinking partner:

| Command | What it does |
|---|---|
| `/context` | Loads full life and work state |
| `/today` | Pulls calendar, tasks, daily notes → prioritized plan |
| `/trace` | Tracks how an idea has evolved across notes over time |
| `/connect` | Bridges two domains using the vault's link graph |
| `/ghost` | Answers a question the way Vin would (uses vault to calibrate voice) |
| `/challenge` | Pressure-tests current beliefs against vault content |
| `/drift` | Surfaces ideas you've circled without committing to |
| `/ideas` | Generates actionable ideas from vault patterns |
| `/graduate` | Promotes a raw note to a structured wiki page |

These are not general-purpose AI tools — they are personalized to the vault's content. They get more powerful as the vault grows.

### Strict human-vs-agent write separation

A principle Vin considers non-negotiable: **never let the agent write into the human-written layer.**

- Human-written: raw sources, daily notes, personal reflections — immutable
- Agent-written: wiki pages, summaries, synthesis — the compiled layer

Mixing them corrupts the source of truth. If the agent modifies a raw note, it's impossible to know which parts are original insight and which are AI interpolation. The separation preserves provenance permanently.

### Writing as the engine

The system's output quality is directly proportional to the quality and quantity of human input. A sparse vault produces generic responses. A rich vault — years of daily notes, project logs, article reactions — produces deeply personalized, contextually accurate responses.

This is the reason 99.99% of people won't build this: it requires sustained writing practice, not just a one-time setup.

### Vault as relationship with the agent

From the source: the vault is not a tool — it is the persistent context for an ongoing relationship with an AI. Each session builds on the last. The human doesn't re-explain context; the agent already knows it. Over months and years, this compounds into something qualitatively different from any individual conversation.

## Relevance to this vault

This source is the strongest argument for treating the Obsidian vault as infrastructure worth maintaining over time. The patterns (writing discipline, strict separation, custom skills) are directly applicable. Priority action: establish a writing/reflection practice that feeds the vault consistently.

## See also

- [[claude-code-obsidian-workflow]]
- [[claude-code]]
- [[obsidian]]
- [[llm-wiki-pattern]]
