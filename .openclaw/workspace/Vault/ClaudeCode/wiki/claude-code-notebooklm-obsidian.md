---
title: "Source Summary: Claude Code + NotebookLM + Obsidian = GOD MODE"
type: source-summary
domain: claudecode
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[ClaudeCode/raw/06-03-2026-claude-code-notebooklm-obsidian.md]]"
tags:
  - notebooklm
  - claude-code
  - obsidian
  - skills
  - workflow
  - research
---

# Source Summary: Claude Code + NotebookLM + Obsidian = GOD MODE

**Author:** Chase AI | **Published:** 06-03-2026 | **Format:** YouTube video

A practical walkthrough of composing Claude Code skills into a full research pipeline: YouTube search → NotebookLM analysis → deliverable generation → Obsidian vault storage. The key contribution is the skill composition pattern and how the Obsidian vault enables a self-improving loop.

## Core thesis

Individual Claude Code capabilities (YouTube search, NotebookLM, deliverable generation) are powerful in isolation. Composing them into a single skill — and grounding the whole system in an Obsidian vault — creates a self-improving research machine.

## The pipeline

```
1. YouTube search skill        → find relevant videos on a topic
2. NotebookLM skill            → send videos for analysis + deliverable generation
3. Results returned            → Claude Code receives markdown analysis + infographic/slides
4. Obsidian vault              → stores everything, builds context over time
5. CLAUDE.md                   → updated to reflect how the human likes to work
```

The entire pipeline is wrapped into one super-skill via the skill creator. One command triggers the whole flow.

## Key ideas

### Skill composition via skill creator

The skill creator (`/skill-creator`) generates Claude Code skills from natural language descriptions. Skills can call other skills. This makes complex multi-step workflows composable into a single slash command. The pattern:

1. Build a YouTube search skill
2. Build a NotebookLM skill
3. Use skill creator to compose them into a "YouTube pipeline" super-skill
4. One command, one result

### NotebookLM as free compute

NotebookLM's analysis runs on Google's infrastructure. Token cost to Claude Code at analysis time is near zero — only the final result is returned. For heavy analysis tasks (summarizing 50 videos, generating slide decks), this is significant. See [[notebooklm-integration]] for the full technical setup.

### The self-improving loop

The Obsidian vault accumulates context across sessions. CLAUDE.md grows to reflect the human's preferences. Over time:
- Analysis improves because Claude Code knows how the human wants results structured
- Deliverables improve because the CLAUDE.md captures format preferences
- The human spends less time steering per session

From the source: "Doing that over a week won't have much effect. Doing it over a year and hundreds of documents — that will have a huge lasting effect."

### CLAUDE.md as "brain within a brain"

If the Obsidian vault is the second brain, CLAUDE.md is the brain within the brain. It tells Claude Code what the vault means — conventions, output format preferences, how to communicate. Updating CLAUDE.md after sessions ("update CLAUDE.md to reflect my preferences from our latest conversations") is the core maintenance operation.

## Limitations of this source

Focused on content creation use case (YouTube research for content strategy). The general pattern applies to any domain but the specific skills shown need adaptation. The `notebooklm-py` library is unofficial and may break.

## See also

- [[notebooklm]]
- [[notebooklm-integration]]
- [[claude-code-obsidian-workflow]]
- [[claude-code]]
- [[llm-wiki-pattern]]
