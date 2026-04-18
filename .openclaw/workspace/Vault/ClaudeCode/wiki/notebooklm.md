---
title: NotebookLM
type: entity
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[Claude Code + NotebookLM + Obsidian = GOD MODE]]"
  - "[[Claude Code + Karpathy's Obsidian = New Meta]]"
tags:
  - notebooklm
  - google
  - research
  - analysis
---

# NotebookLM

Google's AI-powered research tool that can ingest up to 50 sources and produce structured analysis, summaries, and multimedia deliverables.

## Capabilities

- **Source ingestion:** YouTube videos, Google Drive files, PDFs, text, copy-paste (up to 50 per notebook)
- **Analysis:**
  - **Cross-document synthesis:** Summarize patterns across multiple whitepapers.
  - **Artifact Generation:** Dynamic flashcards, quizzes, audio podcasts, study guides.
  - **Accelerated Consumption (Just In Time vs Just In Case):** Generate targeted briefings and study aids from custom sources right before decision-making, rather than consuming general information speculatively (concept by [[dan-martell-smart-with-ai|Dan Martell]]).
- **Deliverables:**
  - Audio overview (podcast-style)
  - Mind maps
  - Flashcards
  - Infographics
  - Slide decks
  - Structured markdown analysis

## Programmatic Access

No official API exists. Integration with [[claude-code]] uses `notebooklm-py` (GitHub: `teng-lin/notebooklm-py`), an unofficial Python wrapper that reverse-engineers the web interface.

**Setup:** `pip install notebooklm-py` -> `notebooklm login` -> browser auth -> ready.

See [[notebooklm-integration]] for the full integration pattern.

## Role in the Workflow Stack

From [[2026-04-10-karpathy-obsidian-new-meta|Jack Roberts]]:
- NotebookLM is the "deep dive and research" layer
- Spin up a notebook with sources on a specific topic
- Run analysis (tokens are Google's cost)
- Bring results back to the vault for long-term retention

## Limitations

- Unofficial API may break with Google changes
- Deliverable generation is slow (10-15 min for slide decks)
- No fine-grained control over analysis methodology
- 50 source limit per notebook

## See also

- [[notebooklm-integration]]
- [[claude-code-obsidian-workflow]]
- [[claude-code-notebooklm-obsidian]]
- [[claude-code]]
