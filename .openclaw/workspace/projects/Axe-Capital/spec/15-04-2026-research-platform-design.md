# Axe Capital — Research Platform Design

**Date:** 15-04-2026
**Status:** Approved, ready for implementation planning
**Milestone target:** 4 weeks (by ~13-05-2026)

---

## 1. Goal

Transform the Axe Capital dashboard from a portfolio monitor into a **research-assist platform**: the place where Robert discovers ideas, watches agents think, and reviews decisions.

**Endgame (not this spec):** fully automated loop with cron, Telegram alerts, monthly PDF. This design lays foundations that make the endgame an additive change, not a rewrite.

## 2. Non-Goals

- Live trading execution
- Replacing IBKR — still the broker of record
- Multi-user / multi-portfolio support
- Paid news APIs (free RSS + LLM scoring only, per user direction)

## 3. Architecture

```
 [RSS feeds]      [SEC EDGAR, yfinance]     [IBKR CSV]
      │                    │                      │
      ▼                    ▼                      ▼
 ┌──────────┐        ┌──────────┐          ┌──────────┐
 │ axe_news │        │ axe_alpha│          │axe_portfo│
 │  (new)   │        │ (exists) │          │ (exists) │
 └────┬─────┘        └────┬─────┘          └────┬─────┘
      │                   │                     │
      └───────────────────┴─────────────────────┘
              all agents use axe_core.trace
                          │
                          ▼
                  ┌───────────────┐
                  │ /public/      │   ← all artifacts live here
                  │   portfolio.json
                  │   targets.json
                  │   alpha-latest.json    (new)
                  │   news-latest.json     (new)
                  │   traces/<run-id>.json (new)
                  │   traces/index.json    (new)
                  │   decision-log.jsonl
                  │   health.json
                  └───────┬───────┘
                          │
                  ┌───────▼────────┐
                  │ React dashboard │  (7 panels)
                  └───────┬────────┘
                          │
                  ┌───────▼────────┐   ← added in week 4
                  │ FastAPI (thin) │     /refresh, /trace/stream, /health
                  └────────────────┘
```

**Principles:**
- Every agent writes a **trace file** — structured JSON capturing reasoning, inputs, outputs, rejected options. This is how Panel 6 works without a separate debate engine.
- **Dashboard is always readable from files alone.** Backend is additive — panels must gracefully degrade if the API is down.
- **One orchestrator** (`axe_orchestrator`) is the only thing cron will ever call in the endgame.

## 4. Module Layout

| Module | Purpose | Location |
|---|---|---|
| `axe_core` | Shared utilities: `trace`, filesystem paths, JSON schema helpers | `step0-shared/axe_core/` (NEW package) |
| `axe_coo` | Data pipeline (existing) | `step1-data-foundation/` |
| `axe_alpha` | Alpha Hunter (existing) | `step4-alpha-hunter/` |
| `axe_portfolio` | Portfolio tracker (existing) | `step5-portfolio-tracking/` |
| `axe_news` | RSS ingestion + LLM impact scorer (NEW) | `step2-news/` |
| `axe_dashboard` | React/Vite UI (existing) — artifact home in `step6-dashboard/public/` | `step6-dashboard/` |
| `axe_orchestrator` | CLI + FastAPI backend | `step7-automation/` |

**Note on step numbering:** Existing dirs jump 1→4→5→6→7. `axe_news` slots into `step2-news/` to fill the gap. The numbering reflects build-order history, not a strict dependency chain.

All agent packages depend on `axe_core`. Agent packages do NOT depend on each other.

## 5. Data Contracts

All artifacts live in `step6-dashboard/public/`. Dashboard code does not compute — it only renders.

### 5.1 `alpha-latest.json` (NEW, wraps existing reports)

Symlink or copy of newest `step4-alpha-hunter/reports/YYYY-MM-DD.json`. Shape already exists:

```json
{
  "report_date": "2026-04-12",
  "generated_at": "2026-04-12T01:59:31+03:00",
  "top_opportunities": [
    {
      "ticker": "RTX",
      "opportunity_type": "earnings_drift",
      "thesis": "...",
      "conviction_score": 7,
      "trigger_source": "yfinance_earnings",
      "trigger_data_point": "...",
      "why_retail_is_missing_this": "...",
      "risk_flags": "...",
      "raw_facts": { "...": "..." },
      "base_score": 6.9
    }
  ]
}
```

### 5.2 `news-latest.json` (NEW)

```json
{
  "generated_at": "2026-04-15T09:00:00Z",
  "sources_polled": ["reuters-biz", "bloomberg-mkts", "sec-edgar-8k", "yahoo-ticker:MSFT", "..."],
  "items_in": 412,
  "items_kept": 18,
  "items": [
    {
      "id": "sha1-of-url",
      "title": "...",
      "url": "...",
      "source": "reuters",
      "published_at": "2026-04-15T08:41:00Z",
      "tickers_mentioned": ["MSFT", "GOOG"],
      "portfolio_relevance": "held|watchlist|sector|none",
      "impact_score": 7,
      "impact_rationale": "Why this moves markets or changes a decision",
      "decision_hook": "Consider trimming MSFT if antitrust probe expands | null",
      "scored_by": "claude-haiku-4-5"
    }
  ]
}
```

**Ranking rules (enforced in LLM prompt):**
- Only keep `impact_score >= 6`
- **Explicitly reject**: analyst ratings, price-target changes, generic market commentary, earnings preview speculation
- **Keep**: regulatory actions, M&A, major product/strategy shifts, executive changes, macro events that reshape sector dynamics, concrete litigation/enforcement, supply-chain disruptions

### 5.3 `traces/<run-id>.json` (NEW)

One file per agent run.

```json
{
  "run_id": "alpha-15-04-2026T09-00-00Z",
  "agent": "axe_alpha",
  "started_at": "2026-04-15T09:00:00Z",
  "ended_at":   "2026-04-15T09:01:34Z",
  "status": "success|failed|partial",
  "summary": "Scanned 412 items, surfaced 8 opportunities, 3 filtered by concentration guard",
  "events": [
    {
      "seq": 1,
      "t": "2026-04-15T09:00:00.120Z",
      "step": "scan_edgar_8k",
      "thought": "Looking for insider cluster buys in last 5 days...",
      "io": { "in": {"lookback_days": 5}, "out": {"candidates": 12} },
      "elapsed_ms": 340
    },
    {
      "seq": 2,
      "t": "...",
      "step": "filter_concentration",
      "thought": "Rejecting AAPL — user already overweight US large-cap tech per investor profile",
      "rejected": ["AAPL", "NVDA"]
    },
    {
      "seq": 3,
      "t": "...",
      "step": "llm_summarize",
      "thought": "Summarizing RTX earnings drift into thesis...",
      "io": { "tokens": {"in": 1240, "out": 380}, "model": "gpt-4o-mini" }
    }
  ]
}
```

### 5.4 `traces/index.json` (NEW)

Rolling index of most recent runs. Panels 5 and 6 read this.

```json
{
  "generated_at": "2026-04-15T09:02:00Z",
  "retention": { "max_runs_per_agent": 50, "total_cap": 500 },
  "runs": [
    {
      "run_id": "alpha-15-04-2026T09-00-00Z",
      "agent": "axe_alpha",
      "started_at": "2026-04-15T09:00:00Z",
      "ended_at":   "2026-04-15T09:01:34Z",
      "duration_ms": 94000,
      "status": "success",
      "event_count": 28,
      "summary": "Scanned 412 items, surfaced 8 opportunities",
      "artifact_written": "alpha-latest.json"
    }
  ]
}
```

**Update semantics:**
- File is a single JSON object (NOT JSONL). Rewritten atomically on every run completion by `axe_core.trace.finalize()` — write to `traces/index.json.tmp`, then `rename()`.
- The `runs` array inside is appended to (new run prepended at index 0), sorted newest-first.
- Per-agent cap: keep newest 50 runs each; older trace files AND their entries pruned together.
- Global cap: 500 runs total (safety).
- Pruning runs atomically inside `finalize()`; no external janitor.

### 5.5 `decision-log.jsonl` (EXISTS — extend)

Add two fields if missing on new appends:
- `decision_type`: `"enter"|"exit"|"trim"|"add"|"hold"|"note"`
- `tags`: `["earnings", "risk-review", ...]` (free-form, optional)

Existing entries stay as-is; Panel 7 tolerates missing fields.

### 5.6 `health.json` (EXISTS — extend)

```json
{
  "generated_at": "2026-04-15T09:02:00Z",
  "artifacts": {
    "portfolio":  { "last_refresh": "2026-04-15T08:00:00Z", "age_min": 62, "status": "fresh|stale|missing" },
    "alpha":      { "...": "..." },
    "news":       { "...": "..." },
    "traces":     { "...": "..." }
  },
  "freshness_thresholds_min": { "portfolio": 240, "alpha": 1440, "news": 60 }
}
```

## 6. Dashboard Panel Mapping

| # | Current component | Becomes | Action |
|---|---|---|---|
| 1 | `PortfolioPanel.jsx` | **Portfolio State** | Keep; add freshness badge from `health.json` |
| 2 | `TargetsPanel.jsx` | **Watchlist & Targets** | Finalize avg-cost-vs-last semantics; explicit UI copy ("% from avg cost" vs "% from last") |
| 3 | `RiskPanel.jsx` | **Alpha Opportunities** | DELETE Risk; build new Alpha panel reading `alpha-latest.json`. Risk metrics fold into Panel 1 |
| 4 | `ResearchPanel.jsx` | **Hot News** | DELETE Research; build new News panel reading `news-latest.json` |
| 5 | `AutomationPanel.jsx` | **Agent Status Board** | Rebuild reading `health.json` + `traces/index.json` |
| 6 | — | **Internal Dialogue Viewer** | NEW; reads `traces/<run-id>.json` — step-by-step thought playback |
| 7 | `DecisionLogPanel.jsx` + `RunbookPanel.jsx` | **Decision Archive** | Merge; filter/search over `decision-log.jsonl`. Delete `RunbookPanel` |

## 7. Testing

- **Python:** pytest with mocked RSS + mocked LLM for `axe_news`; unit tests for `axe_core.trace` emit/finalize/prune; CLI tests for `axe_orchestrator`
- **Dashboard:** no unit tests; manual verification in dev server per panel against fixture JSON
- **Integration:** `axe_orchestrator run-all` against real sources, verify `/public/*.json` files validate against their schemas

## 8. Milestones

**Week 1 — Foundations** (by 22-04-2026)
- `axe_core` package scaffold + `trace` lib (emit + finalize + prune)
- Wire `trace` into `axe_alpha` and `axe_portfolio`
- Freeze data contracts in code (pydantic schemas or JSON Schema files)
- `axe_orchestrator` CLI skeleton: `run alpha|news|portfolio|all`
- Panel 2 (Targets) semantics finalized in UI

**Week 2 — Research content panels** (by 29-04-2026)
- Panel 3 Alpha Opportunities
- Panel 7 Decision Archive
- `axe_news`: RSS ingestion + LLM scorer (Haiku 4.5 with prompt caching)

**Week 3 — Observability panels** (by 06-05-2026)
- Panel 4 Hot News
- Panel 5 Agent Status Board
- Panel 6 Agent Trace Viewer

**Week 4 — Backend & endgame handoff** (by 13-05-2026)
- FastAPI: `/health`, `/refresh/{agent}`, SSE `/trace/stream/{run_id}`
- Dashboard: uses API when available, falls back to files
- Documented cron + Telegram integration paths (NOT scheduled; that's endgame)

## 9. Definition of Done (B-milestone)

- All 7 panels populated with real, current data from a fresh `run-all`
- User can trigger a refresh from the dashboard (via FastAPI)
- User can watch an agent think in real time (Panel 6 with SSE)
- User can browse any past decision and jump to the trace that produced it
- `axe_orchestrator run-all` exits 0 on a clean box with only fresh IBKR CSV + internet
