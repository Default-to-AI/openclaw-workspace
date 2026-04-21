# Axe Capital Command Center Redesign

Date: 2026-04-21
Status: Proposed
Scope: Step 6 dashboard shell, UX model, frontend aggregation layer, and the backend direction required to support an autonomous firm-style command center.

## Why This Exists

The current dashboard proves the pipeline exists, but it still feels like a set of panels and utility tabs.

That is not the product.

The product is an autonomous research firm with a human operator seat. Agents should scan continuously, launch missions automatically, finish the full pipeline, and leave the operator with a decision, evidence, and a playbook.

This spec redesigns the dashboard around that model.

## Product Definition

Axe Capital is not a button-driven dashboard. It is a hedge-fund-style multi-agent operating system.

The normal system behavior is:

1. Watchers scan continuously for opportunities and portfolio issues
2. A trigger layer deduplicates and scores findings
3. The orchestrator launches a mission automatically
4. Specialists, debate, risk, compliance, and CEO stages run to completion
5. The finished decision lands in the operator inbox

The operator does not babysit the system. The operator reviews completed decisions, inspects live missions, and intervenes only when useful.

## Non-Goals

- No auto-trading
- No “click to run opportunities” primary workflow
- No dev-tool-first UI with raw internal scaffolding exposed as product
- No full backend rewrite before the dashboard shape is corrected

## Core UX Decision

The homepage becomes `Command Center`.

It is a hybrid war room:

- split-screen from first load
- firm-wide by default
- mission takeover when a run becomes active
- decision-first homepage priority

The first question the UI answers is:

`What needs attention now, and what has the firm already concluded?`

## Primary Product Objects

The redesign moves the UI away from equal-weight tabs and generic cards. The app should be organized around these product objects:

- watcher
- trigger
- mission
- decision inbox item
- surveillance alert
- firm exception

These objects map better to an autonomous research firm than “panel”, “tab”, or “refresh target”.

## Homepage Structure

## 1. Decision Inbox

Priority: highest

Purpose:
- show new completed decisions
- show portfolio actions requiring review
- surface the final output of the autonomous firm

Content:
- symbol or portfolio scope
- action vocabulary (`BUY`, `ADD`, `HOLD`, `TRIM`, `SELL`, `TIGHTEN_STOP`, `LOOSEN_STOP`, `REBALANCE`, `WATCH`)
- confidence
- urgency
- source watcher or trigger reason
- timestamp
- quick summary
- click-through to full evidence and playbook

Behavior:
- if urgent decisions exist, they dominate the inbox
- if no urgent decisions exist, the inbox should show the strongest recent decisions or the best current opportunities
- the inbox should feel like an executive operating surface, not a log table

## 2. Live Mission Board

Priority: highest

Purpose:
- show all currently running missions
- make the firm feel alive
- give the operator visibility into autonomous work already underway

Content per mission:
- mission title
- source watcher
- symbol or portfolio issue
- stage progression
- participating agents
- current state (`queued`, `running`, `blocked`, `completed`, `failed`)
- elapsed time
- latest emitted summary

Behavior:
- selecting a mission opens Mission Takeover Mode
- completed missions leave this board and appear in the Decision Inbox / History

## 3. Autonomous Watcher Grid

Purpose:
- make continuous scanning visible
- show that the firm is doing real work in the background

Initial watcher set:
- News Watcher
- Social / Narrative Watcher
- Value / Discount Watcher
- Market Regime Watcher
- Portfolio Surveillance Watcher
- Risk Drift Watcher

Each watcher card shows:
- role
- scope
- cadence
- latest finding
- status
- candidates emitted in recent periods

Important:
- this is not a process-status board
- watcher cards should describe what the watcher sees and finds, not only that a cron job ran

## 4. Portfolio Surveillance Board

Purpose:
- continuously monitor the actual holdings
- show where the portfolio itself is generating missions

Surveillance categories:
- missing stop loss
- missing target
- near stop
- trim candidate
- rebalance candidate
- concentration drift
- stale specialist coverage
- thesis drift
- action mismatch between latest decision and live position state

Behavior:
- alerts can auto-trigger missions
- portfolio surveillance should feel like an always-on risk and discipline layer, not a static holdings table

## 5. Firm Health And Exceptions

Purpose:
- surface only the operational exceptions that matter

Examples:
- blocked mission
- watcher failure
- stale critical artifact
- broker degraded
- API degraded
- queue backlog
- risk/compliance unavailable

Important:
- this is not a developer diagnostics screen
- raw internal status belongs in drill-downs, not in the main operator surface

## Mission Takeover Mode

When a mission is selected or becomes the current focus, the center of gravity shifts from firm-wide mode to a dedicated war room.

Left column:
- mission brief
- trigger reason
- source watcher
- symbol or portfolio issue
- key facts
- current stage and timeline

Right column:
- live agent lanes
- streamed outputs
- specialist summaries
- bull thesis
- bear thesis
- devil’s advocate
- risk manager
- compliance / audit
- CEO decision
- final playbook

Bottom rail:
- trace
- evidence links
- source documents
- related past missions
- related existing holdings

The mission takeover view should preserve some compressed firm context so the operator never feels disconnected from the broader system.

## Navigation Model

The app should no longer lead with the old equal-priority utility tabs.

Recommended navigation:

- Command Center
- Portfolio
- Research
- Missions
- History
- Ops

Definitions:
- `Command Center` is the homepage and default operator seat
- `Portfolio` is the detailed position and surveillance workspace
- `Research` is the library of opportunities, reports, and specialist outputs
- `Missions` is the focused run browser
- `History` is the decision archive and longitudinal memory
- `Ops` is exception handling and lower-level system status

## Manual Controls

Manual controls stay in the product, but they are not the primary workflow.

Allowed primary manual actions:
- pause
- rerun
- inspect
- escalate
- archive
- acknowledge

Allowed secondary manual actions:
- force refresh
- manual mission launch for debugging or exploration

Important:
- `Run Opportunities` should not be a homepage CTA
- if retained, it belongs in Ops or an overflow menu as a manual override

## Visual Direction

The aesthetic target is a premium institutional command room, not a generic AI dashboard.

Visual qualities:
- dark graphite / navy foundation
- sharp signal colors used sparingly
- mono + editorial typography pairing
- dense but deliberate spacing
- stronger hierarchy than the current card grid
- more cinematic and professional without becoming noisy

Avoid:
- purple gradient startup-app aesthetics
- generic Tailwind card farms
- raw developer panels presented as investor-facing product
- decorative motion without signal value

## Responsive Behavior

Desktop:
- split-screen command deck plus live mission floor
- multiple simultaneous surfaces visible

Tablet:
- stack major surfaces more aggressively
- preserve decision inbox and live mission board near the top

Mobile:
- do not preserve the desktop shell
- stack the command hierarchy vertically
- Decision Inbox and current mission summary come first
- watcher grid and surveillance condense into scrollable sections

## Data Model Bridge

The dashboard should not wait for a full backend redesign before it adopts the correct product shape.

Add a frontend aggregation layer that maps existing artifacts into the new objects:

- `portfolio.json` + `position-state.json` -> surveillance alerts
- `decision-latest.json` + archive logs -> decision inbox items
- `traces/index.json` + trace artifacts -> missions and mission stage progress
- `health.json` -> firm exceptions and freshness
- `analyst-reports/index.json` -> specialist evidence cards
- committee run traces -> mission takeover content

This bridge lets Step 6 adopt the correct model immediately while Step 7 evolves in parallel.

## Backend Direction

The backend should move toward first-class autonomous runtime concepts.

Required runtime concepts:
- watcher jobs
- candidate queue
- trigger scoring
- deduplication
- mission launcher
- mission lifecycle state
- completed decision inbox feed

Target operating model:
- watchers run continuously
- triggers score and suppress noise
- missions launch automatically
- missions run the full pipeline to completion
- decisions land in the inbox without operator intervention

## Role Alignment

The UI and runtime should treat the firm as a company with named roles.

Visible roles:
- CEO
- COO / CFO
- Portfolio Manager
- Risk Manager
- Fundamental Analyst
- Technical Analyst
- Macro Strategist
- Compliance / Audit
- Bull
- Bear
- Devil’s Advocate

Current gap:
- Risk Manager is partial
- Compliance / Audit is missing

Design implication:
- the UI must make room for these roles now, even if some are initially backed by placeholder or partial data
- the dashboard should not freeze the product around the current incomplete implementation

## What Stays

Keep:
- artifact-first boundary under `step6-dashboard/public/`
- committee orchestration and SSE streaming
- analyst report artifacts
- trace infrastructure
- decision archive idea
- current portfolio ingestion fallback chain

## What Gets Demoted Or Removed

Demote from primary UI:
- manual `Run Opportunities`
- developer-looking process boards
- raw internal dialogue panels
- utility-first refresh controls as the main interaction model

Remove as product framing:
- “dashboard as the product”
- equal-weight tabs for all surfaces

## First Implementation Slice

Implement first:

### Slice 1 — Command Center Shell

Deliver:
- new homepage layout
- Decision Inbox
- Live Mission Board
- Watcher Grid
- Portfolio Surveillance Board
- Firm Health And Exceptions
- stronger visual system and layout shell
- mobile-safe responsive behavior

### Slice 2 — Frontend Aggregation Layer

Deliver:
- object mappers for missions, inbox items, watcher cards, surveillance alerts, exceptions
- bridge current artifacts into the new surfaces

### Slice 3 — Backend Autonomy Upgrade

Deliver:
- watcher jobs
- trigger engine
- candidate queue
- automatic mission launch
- auto-finish to decision inbox

Rationale:
- Slice 1 and Slice 2 change the product shape immediately
- Slice 3 then makes the live system behavior match the new UI

## Success Criteria

The redesign is successful when:

- the app opens to Command Center, not a passive report page
- the homepage tells the operator what matters now
- autonomous work is visible without button babysitting
- missions feel like first-class objects
- portfolio surveillance feels always-on
- completed decisions are easy to review
- manual controls are overrides, not the default workflow
- the app feels like a professional command center rather than a prototype panel collection

## Risks

### Risk 1: frontend redesign outruns backend reality
Mitigation:
- use the aggregation bridge
- stage the redesign around current artifacts first

### Risk 2: the UI becomes visually dramatic but operationally noisy
Mitigation:
- keep decision-first hierarchy
- prioritize attention surfaces over ambient activity

### Risk 3: the system keeps dev-only concepts in investor-facing views
Mitigation:
- demote raw trace/process panels into drill-downs
- keep the main surface operator-facing

## Recommended Next Step

Write the implementation plan for:

`Slice 1 + Slice 2`

Do not wait for full watcher autonomy before rebuilding the shell.
