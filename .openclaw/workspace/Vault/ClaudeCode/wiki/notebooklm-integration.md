---
title: NotebookLM Integration
type: concept
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[Claude Code + NotebookLM + Obsidian = GOD MODE]]"
  - "[[Claude Code + Karpathy's Obsidian = New Meta]]"
tags:
  - notebooklm
  - claude-code
  - research
  - analysis
  - google
---

# NotebookLM Integration

Using Google's [[notebooklm]] as an analysis and deliverable engine within [[claude-code]] workflows.

## Why Integrate NotebookLM

1. **Free compute.** NotebookLM's analysis tokens are Google's cost, not yours. Offloading heavy analysis (summarization, cross-referencing, deliverable generation) saves significant Claude API usage.
2. **Rich deliverables.** NotebookLM can produce podcasts, mind maps, flashcards, infographics, slide decks, and structured analysis -- formats Claude Code cannot natively generate.
3. **Up to 50 sources per notebook.** Can ingest YouTube videos, Drive files, text, PDFs, and more.

## Integration Method

There is no official NotebookLM API. Integration uses `notebooklm-py`, an unofficial Python wrapper.

**Setup:**
1. Install `notebooklm-py` from GitHub (`teng-lin/notebooklm-py`)
2. Run `notebooklm login` to authenticate via browser
3. Create a Claude Code skill for NotebookLM operations (or use the skill creator to generate one)

**Available Operations:**
- Create notebooks
- Add sources (Drive, text, files, YouTube, up to 50)
- Generate deliverables (audio review, mind map, flashcards, infographic, slide deck)
- Retrieve analysis results

## Workflow Pattern

```
Source Discovery (e.g., YouTube search skill)
       |
   NotebookLM (analysis + deliverables)
       |
   Claude Code (receives results, writes to vault)
       |
   Obsidian Vault (persistent storage + cross-linking)
```

This entire pipeline can be composed into a single super-skill via the skill creator. See [[2026-03-06-claude-code-notebooklm-obsidian]] for the full walkthrough.

## Limitations

- `notebooklm-py` is a reverse-engineered wrapper; may break with Google API changes.
- Deliverable generation can take 10-15 minutes (especially slide decks).
- Analysis quality depends on source quality and quantity.
- No fine-grained control over NotebookLM's analysis methodology.

## Role in the Memory Stack

From [[2026-04-10-karpathy-obsidian-new-meta|Jack Roberts' three-layer model]]:
- claude.md = identity
- Obsidian = reasoning (active knowledge)
- Pinecone = recall (static archives)
- **NotebookLM = deep-dive research** (spin up on demand for specific investigations, bring results back to vault)

## See also

- [[notebooklm]]
- [[claude-code-obsidian-workflow]]
- [[claude-code-notebooklm-obsidian]]
- [[claude-code]]
