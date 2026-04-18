# Vault Schema — LLM Wiki

Based on Andrej Karpathy's LLM Wiki pattern.
Claude is the wiki maintainer. Robert curates sources, directs analysis, and asks questions. Claude does all summarizing, cross-referencing, filing, and bookkeeping.

---

## The Core Idea

The vault is a **persistent, compounding knowledge base** — not a RAG system. When a new source arrives, the LLM doesn't index it for later retrieval. It reads it, extracts key information, and integrates it into the wiki — updating entity pages, revising summaries, flagging contradictions. Knowledge is compiled once and kept current.

The wiki grows richer with every source added and every question asked. Cross-references are already there. Contradictions are already flagged. The synthesis already reflects everything ingested.

**Robert's role:** curate sources, direct analysis, ask good questions.  
**Claude's role:** summarizing, cross-referencing, filing, bookkeeping — everything else.

---

## Architecture

Three layers per domain:

| Layer | Location | Owner | Rule |
|---|---|---|---|
| **Raw sources** | `{domain}/raw/` | Robert | Immutable content, but Claude MAY edit metadata and formatting for clarity/consistency: apply relevant tags, rewrite clickbait titles, improve descriptions, strip self-promotion. |
| **Wiki** | `{domain}/wiki/` | Claude | Claude creates, updates, and maintains all pages. Robert reads. |
| **Schema** | This file | Co-evolved | Governs how Claude operates on the vault. |

### Domains

| Domain | Root | Purpose |
|---|---|---|
| Finance | `Finance/` | Investing, markets, portfolio, financial analysis |
| Academia | `Academia/` | College coursework + self-directed intellectual study |
| OpenClaw | `OpenClaw/` | OpenClaw agent framework — setup, efficiency, workflows, project taskboards |
| Claude Code | `ClaudeCode/` | Claude Code, AI tooling, LLM patterns, workflows |
| AI Sphere | `AI Sphere/` | General AI — industry news, research, tools, frameworks, trends (not ClaudeCode/OpenClaw-specific) |
| Life OS | `LifeOS/` | Personal systems, routines, identity, goals |
| Social Media | `SocialMedia/` | Content ideas, posts, engagement strategy |

**Additional layers:**
- `OpenClaw/Projects/<ProjectName>/` — Task tracking and reference material for projects built with OpenClaw agents. Code lives in `workspace/projects/`, the vault holds taskboards and context.

Non-wiki areas: `Archive/` is infrastructure — do not wiki-ify.

---

## Wiki Page Conventions

### Frontmatter (YAML)

Every wiki page starts with:

```yaml
---
title: Page Title
type: entity | concept | source-summary | synthesis | comparison
domain: finance | academia | openclaw | claudecode | lifeos | socialmedia
created: DD-MM-YYYY
updated: DD-MM-YYYY
sources:
  - "[[path/to/raw-source]]"
tags: []
---
```

### Page Types

- **entity** — A person, company, tool, or asset (e.g. `Warren Buffett`, `OpenClaw`, `Interactive Brokers`)
- **concept** — An idea, framework, strategy, or principle (e.g. `Position Sizing`, `Variant Perception`, `Agent Orchestration`)
- **source-summary** — Synthesis of one raw source. Always links back to the raw file.
- **synthesis** — Cross-cutting page integrating multiple sources into an evolving thesis
- **comparison** — Side-by-side analysis of alternatives

### Cross-referencing

- Use `[[wikilinks]]` for all internal references
- Every page links to related pages in a `## See also` section at the bottom
- Every non-trivial claim cites at least one source via `[[raw-source-link]]`

### File Naming

- Lowercase, hyphens for spaces: `position-sizing.md`, `variant-perception.md`
- Source summaries use a descriptive name, no date prefix: `hedge-fund-strategy-research.md`
- Dates belong in frontmatter (`created`, `updated`) only — never in filenames

### Date and Time Format

- Wiki frontmatter, log entries, filenames: **DD-MM-YYYY** (e.g. `12-04-2026`)
- Time: **24-hour format** (e.g. `14:30`)
- **Exception — Obsidian Tasks plugin:** due/done/scheduled dates stay **YYYY-MM-DD** — hard plugin constraint.

---

## Task Workflow (Obsidian)

### Canonical files
- **Inbox (intake):** `/_raw/Tasks/Inbox.md`
  - `## ⚡️ Jinx Claw Tasks` (agent writes here)
  - `## 🧑‍💻 My Tasks (Robert’s manually typed)` (Robert writes here)
- **Master categorized list (canonical):** `/Master_Categorized_Tasks.md`
- **Axe Capital source list:** `/Axe_Capital_Tasks.md`

### Rules
1. New tasks are written only in the Inbox (under the correct header).
2. The agent periodically triages Inbox tasks into `Master_Categorized_Tasks.md` by meaning/keywords.
3. If a category is missing, the agent creates it.
4. Use Obsidian internal links (`[[...]]`) for cross-file references.
5. Do not create task files in the OpenClaw workspace (`10_Tasks/` is deprecated).

---

## Operations

### 1. Ingest
**Canonical intake:** All new sources land in the vault root `/_raw/` folder first (the underscore folder). The agent reviews each item and then moves the original source into the correct domain’s `Domain/raw/` folder.

When Robert adds a new raw source in `/_raw/` (any `.md` file without "(To Ingest)" prefix also counts):
- Also check for ANY uningested `.md` files in `/_raw/` on startup and ingest any found.

When Robert adds a new raw source in `/_raw/`:

1. Read the source completely
2. Clean the source metadata (before creating wiki pages):
   - Apply relevant `tags:` based on content (one tag per line, hyphen prefix)
   - Rewrite clickbait titles to reflect actual content
   - Improve/create description that accurately describes the source
   - Strip any self-promotion content: referral codes, affiliate links, "code X for Y% off" promotional links
   - Strip in-content promotional sections: call-to-action blocks (e.g., "Follow me on...", "Join [X] with code [Y]", "My software/tools/deals", affiliate product links, course/brand promo, generic "like/subscribe" CTAs). Keep brief bio/context ("Why watch?") and chapter markers.
3. Discuss key takeaways with Robert (unless batch mode)
4. Create a **source-summary** page in the relevant `wiki/`
5. Create or update **entity** and **concept** pages touched by the source
6. Update `wiki/index.md` with new/changed pages
7. Append an entry to `wiki/log.md`
8. Update cross-references across all affected pages
9. Move the source to its relevant domain/raw/ folder using DD-MM-YYYY date format (e.g. `11-04-2026-source-title.md`)
10. Log the ingestion in `_raw/ingestion_log.md` with: timestamp, source name, destination domain

_Favour appending to existing concept/entity pages before generating brand new single-paragraph pages._

### 2. Query

When Robert asks a question:

1. Read `wiki/index.md` to find relevant pages
2. Read those pages
3. Synthesize an answer with citations
4. If the answer is reusable, offer to file it as a new wiki page (synthesis or comparison type)

Good answers should be filed back into the wiki — explorations compound the knowledge base just like ingested sources do.

### 3. Lint

Periodic health check. Look for:

- Contradictions between pages
- Stale claims superseded by newer sources
- Orphan pages with no inbound links
- Concepts mentioned but lacking their own page
- Missing cross-references
- Data gaps that could be filled with a web search or new source

---

## Wiki Index and Log

### index.md

Content-oriented catalog of every wiki page. Organized by type (entities, concepts, source summaries, syntheses). Each entry: `- [[page-link]] — one-line summary`. Updated on every ingest. The LLM reads the index first when answering a query, then drills into relevant pages.

### log.md

Chronological, append-only. Format:

```
## [DD-MM-YYYY] action | Subject
Brief description of what changed and which pages were touched.
```

Each entry starts with a consistent prefix so the log is grep-parseable:
`grep "^## \[" wiki/log.md | tail -5` gives the last 5 entries.

---

## Guardrails

- **Never delete raw sources.** They are immutable.
- **Never guess.** State assumptions and ask for confirmation.
- **Preserve provenance.** Every wiki claim traces back to at least one raw source.
- **Prefer incremental updates** over full rewrites of existing wiki pages.
- **Play devil's advocate** on non-trivial claims — note where evidence is weak or contradictory.
- **Keep Robert out of rabbit holes** — push toward KPI-moving work.
- **Fewer, higher-quality pages** over volume. Don't create a page for something that's a footnote.
- **File good answers.** If a query produces a reusable synthesis, offer to write it as a wiki page.
