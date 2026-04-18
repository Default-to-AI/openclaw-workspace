---
title: Claude Code + Obsidian Workflow
type: concept
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[Claude Code + Karpathy's Obsidian = New Meta]]"
  - "[[Claude Code + NotebookLM + Obsidian = GOD MODE]]"
  - "[[How I Use Obsidian + Claude Code to Run My Life]]"
tags:
  - workflow
  - obsidian
  - claude-code
  - knowledge-management
  - personal-os
---

# Claude Code + Obsidian Workflow

The core operating pattern for using Claude Code and Obsidian together as a personal knowledge system. Claude Code runs in the terminal beside an open Obsidian window — the agent writes, the human observes and steers.

## The Setup

```
[Raw sources] → Claude Code reads → [Wiki pages updated] → Obsidian displays
      ↑                                                           ↓
  Robert adds                                           Robert reads, steers,
  new source                                            checks graph view
```

**Three files do most of the work:**
- `CLAUDE.md` — the schema. Tells Claude how the vault is structured, what conventions to follow, what workflows to use. Read first on every session.
- `wiki/index.md` — the catalog. Claude reads this first when answering queries to find relevant pages.
- `wiki/log.md` — the timeline. Append-only record of every ingest and operation.

## Ingest flow (one source at a time)

1. Drop source into `{domain}/raw/`
2. Tell Claude Code to process it
3. Claude reads, extracts key ideas, discusses with Robert
4. Claude writes a source-summary page
5. Claude updates or creates entity/concept pages touched by the source (typically 5–15 pages)
6. Claude updates `wiki/index.md`
7. Claude appends to `wiki/log.md`
8. Robert reviews in Obsidian — graph view shows new nodes and links

## Query flow

1. Robert asks a question
2. Claude reads `wiki/index.md` to identify relevant pages
3. Claude reads those pages
4. Claude synthesizes an answer with citations
5. If the answer is reusable → offer to file it as a synthesis or comparison page

## The compounding effect

Each source enriches multiple pages. Each query can produce a new page. The wiki grows denser with every operation — not just bigger, but more interconnected. This is the key difference from RAG: knowledge is compiled once and kept current rather than re-derived on every query.

## Human-vs-agent separation (Vin's principle)

From [[obsidian-claude-code-run-my-life]]: maintain a strict boundary between human-written notes and agent-written pages. Raw sources and personal reflections stay human-owned and immutable. The wiki is agent-owned. This separation preserves provenance and prevents agent drift from corrupting the source of truth.

## Custom thinking tools (slash commands)

Vin's vault extends this workflow with custom skills that use the vault as context:
- `/trace` — how has an idea evolved across notes over time
- `/connect` — bridge two domains by traversing the link graph
- `/ghost` — answer a question the way the vault owner would
- `/challenge` — pressure-test current beliefs against vault content
- `/ideas` — generate actionable ideas from vault patterns
- `/today` — pull calendar, tasks, and daily notes into a prioritized plan

These turn Claude Code from a generic assistant into a deeply personalized thinking partner. See [[obsidian-claude-code-run-my-life]].

## Scaling boundary

Works well up to ~500–1000 wiki pages. Beyond that, token cost to read `index.md` becomes prohibitive. At that scale, supplement with a vector database for large static archives. See [[llm-wiki-pattern]] for the full scaling analysis.

## See also

- [[claude-code]]
- [[obsidian]]
- [[llm-wiki-pattern]]
- [[notebooklm-integration]]
- [[karpathy-obsidian-new-meta]]
- [[claude-code-notebooklm-obsidian]]
- [[obsidian-claude-code-run-my-life]]
