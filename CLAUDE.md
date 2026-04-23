# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

# gstack

Use the `/browse` skill from gstack for all web browsing. Never use `mcp__claude-in-chrome__*` tools.

## Available gstack skills

- `/browse` — Headless browser for web browsing and QA
- `/office-hours` — YC Office Hours: product decisions and startup strategy
- `/plan-ceo-review` — CEO/founder-mode plan review
- `/plan-eng-review` — Architecture / engineering plan review
- `/plan-design-review` — Designer's eye plan review
- `/plan-devex-review` — Developer experience plan review
- `/ship` — Ship workflow: commit, PR, merge
- `/review` — Pre-landing PR code review
- `/investigate` — Systematic debugging
- `/qa` — QA test a web application
- `/design-review` — Designer's eye visual audit
- `/autoplan` — Auto-review pipeline
- `/document-release` — Post-ship documentation update
- `/learn` — Manage project learnings
- `/codex` — OpenAI Codex CLI wrapper
- `/gstack-upgrade` — Upgrade gstack to latest version

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill tool as your FIRST action. Do NOT answer directly, do NOT use other tools first. The skill has specialized workflows that produce better results.

**gstack:**
- Browse web, open URL, check a live page → `/browse`
- Product ideas, startup strategy, "is this worth building" → `/office-hours`
- Ship code, push, create PR → `/ship`
- Code review, diff review, pre-merge check → `/review`
- Bug, error, "why is this broken", unexpected behavior → `/investigate`
- QA, test the UI, find bugs on a live site → `/qa`
- Post-deploy health check → `/canary`
- Weekly retro → `/retro`
- Update docs after a release → `/document-release`
- Architecture review, eng plan critique → `/plan-eng-review`

**superpowers:**
- Before building any new feature or component → `superpowers:brainstorming`
- Any bug or test failure (before proposing fixes) → `superpowers:systematic-debugging`
- Before writing implementation code → `superpowers:test-driven-development`
- Have a spec, planning a multi-step implementation → `superpowers:writing-plans`
- Executing a written plan → `superpowers:executing-plans`
- About to say "done", before committing or PRing → `superpowers:verification-before-completion`
- Receiving code review feedback → `superpowers:receiving-code-review`
- Feature complete, want a review → `superpowers:requesting-code-review`
- Implementation done, figuring out how to integrate → `superpowers:finishing-a-development-branch`
- 2+ independent tasks that don't depend on each other → `superpowers:dispatching-parallel-agents`
- Feature needs isolated workspace → `superpowers:using-git-worktrees`

**other:**
- Settings.json, hooks, permissions changes → `update-config`
- Token audit, context window issues → `token-optimizer:token-optimizer`
- Build a web UI, component, dashboard → `frontend-design`
- Next.js / Vercel performance → `vercel-react-best-practices`

## Model routing

For subagents and Task calls, assign by task type:
- `haiku` — data gathering: grep, file search, counting, simple lookups
- `sonnet` — editing, code review, explanations, judgment calls (default)
- `opus` — architecture planning, multi-file synthesis, cross-cutting analysis
