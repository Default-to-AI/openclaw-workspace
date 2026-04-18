---
title: ClaudeCode Wiki Log
type: log
domain: claudecode
---

# ClaudeCode Wiki Log

Append-only chronological record of all wiki operations.

## [12-04-2026] init | Wiki initialized
Vault rehaul complete. Wiki structure created for ClaudeCode domain. Existing content migrated from previous numbered folder structure. Ready for ingest.

## [12-04-2026] fix | Structural cleanup — all existing pages
Fixed domain metadata (`ai` → `claudecode`) and dead source paths (`50_AISphere/...` → correct new paths) across all 5 existing wiki pages. Fixed dead wikilinks throughout. Moved misplaced raw sources: TradingView video → `Finance/raw/`; OpenClaw agents video → `OpenClaw/raw/`.

## [12-04-2026] create | New entity pages — claude-code, obsidian
Created `claude-code.md` (entity) and `obsidian.md` (entity). Both were referenced by multiple existing pages but did not exist.

## [12-04-2026] create | New concept page — claude-code-obsidian-workflow
Created `claude-code-obsidian-workflow.md` (concept). Synthesizes the core operating pattern from three sources: Karpathy video, Chase AI video, Greg Isenberg/Vin video. Referenced by 3 existing pages but did not exist.

## [12-04-2026] ingest | Claude Code + Karpathy's Obsidian = New Meta (Jack Roberts, 10-04-2026)
Source: `ClaudeCode/raw/Claude Code + Karpathy's Obsidian = New Meta.md`
Created: `karpathy-obsidian-new-meta.md` (source-summary)
Updated: `llm-wiki-pattern.md` (dead wikilinks resolved), `claude-code-obsidian-workflow.md` (cross-ref added)

## [12-04-2026] ingest | Claude Code + NotebookLM + Obsidian = GOD MODE (Chase AI, 06-03-2026)
Source: `ClaudeCode/raw/Claude Code + NotebookLM + Obsidian = GOD MODE.md`
Created: `claude-code-notebooklm-obsidian.md` (source-summary)
Updated: `notebooklm.md` (dead wikilink resolved), `notebooklm-integration.md` (dead wikilink resolved)

## [12-04-2026] ingest | How I Use Obsidian + Claude Code to Run My Life (Greg Isenberg / Vin, 23-02-2026)
Source: `ClaudeCode/raw/How I Use Obsidian + Claude Code to Run My Life.md`
Created: `obsidian-claude-code-run-my-life.md` (source-summary)
Updated: `claude-code-obsidian-workflow.md` (human-vs-agent separation section, slash commands table), `obsidian.md` (Obsidian CLI section)

## [12-04-2026] update | index.md populated
Added all 8 content pages to index. Domain now fully catalogued.

## [12-04-2026] rename | Removed date prefixes from all wiki filenames
Renamed all date-prefixed source-summary files across ClaudeCode, Finance, and OpenClaw wikis to clean descriptive names. Updated all wikilinks vault-wide.

## [15-04-2026] ingest | claude-routines
New source ingested: Nick Saraev video on Claude Routines. Stripped heavy self-promotion from metadata. Rewrote title to reflect actual content. Added tags. Created source summary `[[claude-routines]]` covering scheduled/webhook/API automations, Gmail/Slack connectors, n8n workflow conversion.

## [16-04-2026] ingest | gstack
New source: Garry Tan's gstack — 23 opinionated Claude Code skills. Stripped clickbait title. Rewrote description. Added tags. Created source summary [[gstack]] and entity [[garry-tan]]. Updated index.md.

## [15-04-2026] ingest | how-claude-code-works
New source from Theo (t3.gg). Stripped sponsor promos (Macroscope). Rewrote title/description. Added tags. Moved to ClaudeCode/raw. Created entity page [[theo]].

## [18-04-2026] ingest | karpathy-claude-code-principles
Source: forrestchang/andrej-karpathy-skills GitHub repo. Stripped Multica/Twitter promo block. Rewrote title/description. Added tags. Created source summary `[[karpathy-claude-code-principles]]` — four principles (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution). Created entity page `[[andrej-karpathy]]`. Updated `[[llm-wiki-pattern]]` cross-references. Updated index.md.
