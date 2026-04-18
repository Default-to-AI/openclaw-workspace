---
title: Obsidian
type: entity
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[How I Use Obsidian + Claude Code to Run My Life]]"
  - "[[Claude Code + Karpathy's Obsidian = New Meta]]"
tags:
  - obsidian
  - markdown
  - knowledge-management
  - pkm
  - tools
---

# Obsidian

A local-first markdown note-taking app built on top of a folder of plain `.md` files. Its defining feature is bidirectional linking — notes reference each other via `[[wikilinks]]`, creating a navigable knowledge graph visible in the graph view.

## Why it matters for AI workflows

Obsidian is not an AI tool — it is a **visualization and navigation layer** for markdown files. The combination with Claude Code is powerful because:

1. **Markdown files are the native format of LLMs.** Claude reads and writes `.md` files natively. No export, conversion, or API needed.
2. **The vault is just a folder.** Claude Code can read, write, and navigate it using standard filesystem operations.
3. **Wikilinks create a queryable graph.** Cross-references written by Claude Code appear as linked nodes in Obsidian's graph view, giving the human a visual map of the knowledge base.
4. **Obsidian CLI** (plugin) exposes file relationships programmatically — Claude can see not just files but which notes link to which.

## Key capabilities used in this vault

- **Graph view:** visualize which wiki pages are hubs, which are orphans, which clusters form
- **Backlinks panel:** see every page that references a given page
- **Dataview plugin:** query frontmatter metadata dynamically (tables, lists, counts)
- **Tasks plugin:** surface tasks embedded anywhere in the vault
- **Web Clipper:** browser extension to clip articles directly into `raw/` as markdown

## Obsidian CLI (plugin)

Extends Obsidian's API to give external agents (like Claude Code) access to vault metadata — not just file contents but the link graph. Enables commands like `/connect` (bridge two domains by traversing the link graph) and `/trace` (how an idea evolved across notes over time). See [[obsidian-claude-code-run-my-life]].

## The "IDE for the wiki" mental model

From Karpathy: *"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."* Claude Code makes edits; the human reviews results in Obsidian in real time — following links, checking the graph, reading updated pages.

## See also

- [[claude-code]]
- [[llm-wiki-pattern]]
- [[claude-code-obsidian-workflow]]
- [[obsidian-claude-code-run-my-life]]
