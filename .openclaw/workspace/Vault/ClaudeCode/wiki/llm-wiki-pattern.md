---
title: LLM Wiki Pattern
type: concept
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[Claude Code + Karpathy's Obsidian = New Meta]]"
  - "[[How I Use Obsidian + Claude Code to Run My Life]]"
tags:
  - llm-wiki
  - karpathy
  - rag
  - knowledge-management
  - obsidian
---

# LLM Wiki Pattern

The LLM Wiki pattern, popularized by Andrej Karpathy, is an alternative to traditional RAG where an LLM incrementally builds and maintains a persistent wiki -- a structured collection of markdown files -- rather than retrieving raw documents at query time.

## How It Works

Instead of: query -> chunk retrieval -> stitch answer -> forget

The wiki pattern: new source -> update 10-15 wiki pages -> knowledge persists -> every future query reads from compiled wiki

### Three-Layer Architecture

| Layer | Contents | Mutability |
|---|---|---|
| **Raw sources** | Articles, PDFs, transcripts, web clips | Immutable (append-only) |
| **Wiki** | LLM-written summaries, concept pages, entity pages | Updated on every ingest |
| **Schema/rulebook** | Conventions, page types, workflows, CLAUDE.md | Rarely changed |

### Three Operations

1. **Ingest** -- Drop a new source; LLM reads it, updates all related wiki pages, logs changes.
2. **Query** -- Ask a question; LLM reads index.md, selects relevant pages, reasons over loaded content.
3. **Lint** -- Periodic maintenance: find contradictions, orphan pages, stale claims, broken links.

## Why It Compounds

- Each source enriches multiple pages, not just one.
- Contradictions between old and new information get flagged.
- Cross-references (wikilinks) build a navigable knowledge graph.
- The index.md provides a constant catalog for the LLM to navigate.

## Scaling Limitations

The pattern scales linearly with file count because there is no semantic search -- the LLM must scan index.md (and sometimes follow links) using raw token reads.

| Files | Approximate index tokens | Cost profile |
|---|---|---|
| 100 | ~7,500 | Comfortable |
| 1,000 | ~75,000 | Noticeable |
| 10,000 | ~750,000 | Impractical |

For large static archives (YouTube transcripts, email history, research papers), a vector database like Pinecone is more appropriate. See the three-layer memory model in [[2026-04-10-karpathy-obsidian-new-meta]].

## When to Use

- Active projects, decision logs, evolving knowledge
- Domains where structure and relationships matter
- Anywhere you need the LLM to *reason over* information, not just recall it

## When NOT to Use

- Large static archives (use vector DB)
- Single-use lookups (just search)
- Datasets exceeding ~500-1000 files

## Implementation in This Vault

This wiki itself follows the LLM Wiki pattern. See the schema in [[ClaudeCode/wiki/index|index]] and the operational log in [[ClaudeCode/wiki/log|log]].

## See also

- [[andrej-karpathy]]
- [[karpathy-claude-code-principles]]
- [[claude-code-obsidian-workflow]]
- [[obsidian]]
- [[karpathy-obsidian-new-meta]]
- [[obsidian-claude-code-run-my-life]]
