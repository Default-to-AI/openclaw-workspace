---
title: Karpathy-Inspired Claude Code Principles
type: source-summary
domain: claudecode
created: 18-04-2026
updated: 18-04-2026
sources:
  - "[[ClaudeCode/raw/16-04-2026-karpathy-claude-code-principles]]"
tags:
  - claude-code
  - karpathy
  - coding-guidelines
  - llm-patterns
  - best-practices
---

# Karpathy-Inspired Claude Code Principles

Forrest Chang's distillation of Andrej Karpathy's post on LLM coding pitfalls into a single CLAUDE.md. The four principles map directly to the behavioral guidelines in Robert's global CLAUDE.md — this source is the origin of that structure.

## The Problems (Karpathy's Diagnosis)

> "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should."

> "They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do."

> "They still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task."

Three failure modes: assumption drift, overengineering, and collateral damage.

## The Four Principles

### 1. Think Before Coding
**Don't assume. Surface tradeoffs. Ask when confused.**

LLMs silently pick an interpretation and run with it. Force explicit reasoning: state assumptions, present multiple interpretations, push back when a simpler path exists, stop when confused.

### 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**

No unasked-for features, no premature abstractions, no hypothetical error handling. The test: would a senior engineer call this overcomplicated? If yes, rewrite it.

### 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**

Don't improve adjacent code. Match existing style. Only remove orphans YOUR changes created — not pre-existing dead code. Every changed line should trace to the user's request.

### 4. Goal-Driven Execution
**Transform imperative tasks into verifiable success criteria.**

"Fix the bug" → "Write a test that reproduces it, then make it pass." Strong criteria let the LLM loop independently. Weak criteria ("make it work") require constant hand-holding.

## The Core Karpathy Insight

> "LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go."

This flips the interaction model: instead of prescribing steps, declare the outcome. The LLM figures out the path. This is most powerful for multi-step tasks where the exact procedure isn't known upfront.

## Tradeoff

These guidelines bias toward caution over speed. For trivial tasks (typo fix, one-liner), full rigor isn't needed. The payoff is on non-trivial work where assumption drift and overengineering compound into expensive rewrites.

## Connection to This Vault

These four principles are already embedded in Robert's global CLAUDE.md, governing all Claude Code sessions. This source provides the origin context and Karpathy's original diagnosis that motivated them.

## See also

- [[andrej-karpathy]]
- [[llm-wiki-pattern]]
- [[claude-code]]
- [[karpathy-obsidian-new-meta]]
