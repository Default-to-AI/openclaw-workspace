# Axe Capital — Delivery Plan

**Owner:** Jinx Claw
**Project manager:** Jinx Claw
**Date:** 2026-04-15
**Current mode:** Build toward visible prototype, then functional prototype, then stable operator alpha.

---

## North Star

Build a research platform that is:
- **functional**: real artifacts, real refresh flow, real trace visibility
- **readable**: one coherent dashboard, not stitched widgets
- **convenient**: easy to launch, easy to refresh, easy to understand what matters
- **trustable**: explicit freshness, explicit status, explicit audit trail

---

## Phase 1 — Visible Prototype

**Target:** today, once launched in the real runtime

### Success criteria
- Dashboard opens locally
- User can see:
  - Portfolio State
  - Watchlist & Targets
  - Alpha Opportunities
  - Hot News (if artifact exists)
  - Agent Status Board
  - Internal Dialogue Viewer shell
  - Decision Archive
- Top system state bar visible
- Layout feels coherent, not placeholder-level chaos

### Remaining work
- Launch in real runtime
- Fix any build/runtime errors
- Confirm panels render from file artifacts without backend

---

## Phase 2 — Functional Prototype

**Target:** same day to next day after runtime validation

### Success criteria
- FastAPI backend runs
- Refresh buttons work
- `axe run all` updates artifacts
- Health status updates correctly
- Trace viewer can open real trace files
- News artifact generation confirmed in a real run

### Remaining work
- Runtime validation outside sandbox
- End-to-end fresh run
- Edge-case cleanup on API fallback / missing artifacts

---

## Phase 3 — Stable Operator Alpha

**Target:** 2 to 5 days depending on runtime issues

### Success criteria
- Daily refresh path is reliable
- Decision archive is useful, searchable, and trace-linked
- Agent traces are readable enough for real review
- Dashboard feels like one product
- Cron path documented and ready
- Telegram alert path documented and ready

### Remaining work
- Polish archive trace linking
- Finish panel consistency pass
- Harden errors / empty states / stale-state handling
- Validate automation scripts in real environment

---

## Immediate priorities (strict order)

### Priority 1 — Make it visible
- Boot API + dashboard
- Fix runtime errors
- Confirm prototype is visible

### Priority 2 — Make it real
- Run refresh end-to-end
- Produce fresh artifacts
- Verify health + trace + news

### Priority 3 — Make it clean
- Remove legacy dead panels
- Extract shared utilities
- Tighten UX consistency and edge states

---

## What I need from Robert

### Minimum unblock
Run the prototype launch steps in the real environment and send me:
- API terminal output
- dashboard terminal output
- browser screenshot if it opens
- any errors exactly as shown

### Nice to have
Answer these product questions:
1. **Desktop-first or mobile-first for v1?** I recommend desktop-first.
2. **Private ops terminal aesthetic or cleaner investor-style aesthetic?** I recommend private ops terminal with cleaner typography.
3. **Do you want the first usable prototype optimized for your current holdings workflow, or for alpha discovery first?** I recommend current holdings workflow first.

---

## Default decisions unless Robert overrides

- **Desktop-first**
- **Dark ops dashboard aesthetic**
- **Current holdings + monitoring first, alpha discovery second**
- **File-first reliability over premature backend complexity**
- **Readable audit trail over flashy UI**

---

## My next actions

1. Continue cleanup and reduce ambiguity in the dashboard codebase
2. Remove legacy components that conflict with the new architecture
3. Prepare for first real launch and runtime debug loop
