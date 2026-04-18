---
title: "Source Summary: Claude Code + Karpathy's Obsidian = New Meta"
type: source-summary
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[ClaudeCode/raw/10-04-2026-karpathy-obsidian-new-meta.md]]"
tags:
  - karpathy
  - llm-wiki
  - obsidian
  - rag
  - memory
  - pinecone
---

# Source Summary: Claude Code + Karpathy's Obsidian = New Meta

**Author:** Jack Roberts | **Published:** 10-04-2026 | **Format:** YouTube video

Jack Roberts walks through Karpathy's LLM Wiki pattern and extends it with a critical analysis of its limits and a three-layer memory architecture that addresses them.

## Core thesis

The LLM Wiki pattern (Karpathy) builds a compounding personal Wikipedia. Each new source updates 5–15 wiki pages rather than being indexed for later retrieval. The result gets smarter with every addition — contradictions flagged, cross-references maintained, synthesis pre-built.

Roberts adds: **the pattern has real limits**, and understanding them determines whether you build something that stays useful or collapses under its own weight.

## Key ideas

### The compounding advantage over RAG

| Traditional RAG | LLM Wiki |
|---|---|
| Query → chunk retrieval → answer → forget | Source → 5–15 pages updated → knowledge persists |
| Starts from scratch every query | Builds on prior work every session |
| No contradiction detection | Contradictions flagged on ingest |

### Three-layer architecture (Karpathy)

1. **Raw sources** — immutable input; articles, PDFs, transcripts
2. **Wiki** — LLM-written, structured, interlinked markdown pages
3. **Schema (CLAUDE.md)** — the rulebook; turns the LLM into a disciplined wiki maintainer

### Four-layer memory model (Roberts' extension)

| Layer | Tool | Mental model | What it stores |
|---|---|---|---|
| Identity | CLAUDE.md | Badge | Who you are, your rules |
| Reasoning | Obsidian wiki | Workshop | Active projects, evolving knowledge |
| Recall | Pinecone (vector DB) | Warehouse | Large static archives |
| Deep research | NotebookLM | Lab | On-demand deep-dive investigations |

The key insight: **Obsidian is for reasoning over structure; Pinecone is for recalling exact text at scale.** Obsidian answers "which hypothesis did I revise after customer 5?" Pinecone answers "find every mention of X across 10,000 documents."

### Scaling limits of the wiki pattern

The LLM must read `index.md` on every query — cost scales linearly with file count:

| Files | ~Index tokens | Profile |
|---|---|---|
| 100 | ~7,500 | Fine |
| 1,000 | ~75,000 | Noticeable |
| 10,000 | ~750,000 | Impractical |

For large static archives (YouTube transcripts, email history, books), use a vector database instead. The wiki pattern is for active, evolving knowledge — not static archives.

### Practical tips

- **Obsidian Web Clipper:** browser extension to clip articles directly to `raw/` as markdown
- **Download images locally** (Settings → Files and links → attachment folder path): lets the LLM view images directly rather than relying on URLs that may break
- **Run two screens:** Claude Code terminal on one side, Obsidian graph view on the other — watch nodes light up in real time as Claude writes pages

## Limitations of this source

This is a commentary/tutorial video, not a primary source. Roberts paraphrases Karpathy's original GitHub write-up — some details may be simplified or slightly reframed. The Pinecone integration he recommends adds operational complexity and cost. For Robert's vault at current scale (~50–200 pages), the Obsidian-only approach is sufficient.

## See also

- [[llm-wiki-pattern]]
- [[claude-code-obsidian-workflow]]
- [[notebooklm-integration]]
- [[obsidian]]
