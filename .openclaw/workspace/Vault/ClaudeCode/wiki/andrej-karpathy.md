---
title: Andrej Karpathy
type: entity
domain: claudecode
created: 18-04-2026
updated: 18-04-2026
sources:
  - "[[ClaudeCode/raw/10-04-2026-karpathy-obsidian-new-meta]]"
  - "[[ClaudeCode/raw/16-04-2026-karpathy-claude-code-principles]]"
tags:
  - karpathy
  - ai-researcher
  - llm-wiki
  - claude-code
---

# Andrej Karpathy

AI researcher and educator. Founding member of OpenAI, then Director of AI at Tesla (Autopilot), returned to OpenAI, then departed to pursue independent research and education.

Known for making foundational AI concepts accessible — "Neural Networks: Zero to Hero" (YouTube series building transformers from scratch) is the canonical self-study path for LLM internals.

## Key Contributions Relevant to This Vault

### LLM Wiki Pattern
Karpathy popularized using an LLM to incrementally build and maintain a persistent wiki rather than re-deriving knowledge from raw documents on every query. This is the foundational pattern behind the structure of this vault. See [[llm-wiki-pattern]].

### Claude Code Coding Principles
Karpathy posted a thread diagnosing three failure modes of LLM coding agents: assumption drift, overengineering, and collateral damage. This diagnosis was distilled by forrestchang into four principles (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) — the same structure in Robert's global CLAUDE.md. See [[karpathy-claude-code-principles]].

Key insight from the post:
> "LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go."

## See also

- [[llm-wiki-pattern]]
- [[karpathy-obsidian-new-meta]]
- [[karpathy-claude-code-principles]]
- [[claude-code-obsidian-workflow]]
