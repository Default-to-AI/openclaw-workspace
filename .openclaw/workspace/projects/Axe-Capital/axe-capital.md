# axe-capital.md — Project Spec v2.0
**Status**: Planning → Build  
**Owner**: Robert  
**Last updated**: 2026-04-11

---

## What This Is

Axe Capital is an autonomous multi-agent research platform that hunts for market-beating opportunities where retail investors don't look. It scrapes the internet, reads financials, monitors news and social media, runs structured internal debates, and produces a professional decision memo for Robert to act on manually at IBKR.

**Core thesis**: Retail doesn't do exhaustive multi-source research. Most are reading the same headlines. Axe Capital's edge is depth, speed, and adversarial structure — every bull case is challenged by a dedicated bear before it reaches Robert.

**Robert's role**: Review. Decide. Execute. He never delegates the trade itself.

---

## What It Is NOT

- Not an automated trader
- Not a black box — every decision includes full reasoning chain and agent dialogue
- Not passive — agents actively hunt for opportunities, not just respond to Robert's queries
- Not Claude-dependent — gpt-4o / gpt-4o-mini only (OpenAI via OpenClaw)

---

## Investment Philosophy

| Parameter | Setting |
|---|---|
| Universe | US equities |
| Style | Active, opportunistic — news-driven, fundamental, technical convergence |
| Horizon | Medium-term (days to months). Not day trading. |
| Benchmark | S&P 500 (SPY). Every trade must justify beating doing nothing. |
| Risk | Capital preservation first. No leverage. No margin. Hard stop-losses. |
| Edge | Multi-source research + adversarial debate + sectors retail ignores |

---

## Agent Org Chart

```
                    ┌────────────────────┐
                    │        CEO         │
                    │  Decision Synth    │
                    └─────────┬──────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
  ┌────────▼───────┐  ┌───────▼──────┐  ┌───────▼──────┐
  │ CIO / Portfolio│  │     CRO      │  │  COO / Data  │
  │    Manager     │  │ Risk Officer │  │    Agent     │
  └────────┬───────┘  └──────────────┘  └──────────────┘
           │
  ┌────────▼──────────────────────────┐
  │            Analyst Team           │
  │ Fundamental | Technical |         │
  │ Sentiment   | Macro     |         │
  │ Alpha Hunter (proactive scan)     │
  └────────┬──────────────────────────┘
           │
  ┌────────▼──────────────┐
  │  Bull / Bear Debate   │
  └────────┬──────────────┘
           │
    [CIO] → [CRO] → [CEO] → Robert
```

---

## Agent Roster

### CEO — Decision Synthesizer
- Reads all downstream memos. No emotion. Macro lens. Final word.
- Output: Structured decision memo (see format below)
- Model: **gpt-4o**
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.
- Apply the 6-step decision framework from `INVESTOR_PROFILE.md` on every decision: portfolio health check, weighted scoring (Fundamental 35%, Macro 25%, Technical 20%, Sentiment 20%), minimum threshold 6.5/10, conviction-based position sizing, VIX-based regime rules, and the hishtalmut priority rule including the 2026 remaining room of ₪19,800 before any new IBKR trade unless conviction is 9+.

### CIO — Portfolio Manager
- Manages book construction: concentration, correlation, sector exposure
- Monitors open positions — flags approaching targets or stops
- Produces trade proposal consumed by CRO and CEO
- Model: **gpt-4o**
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

### CRO — Risk Officer
- Hard rules enforced before CEO sees anything: max 20% per position, no adding to losers, mandatory stop-loss on every entry, liquidity check, VIX context
- Output: APPROVED / BLOCKED / CONDITIONAL
- Model: **gpt-4o**
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

### COO — Data Agent
- Runs first. Fetches and normalizes all data. Packages bundles per analyst.
- Flags stale or missing data before analysis begins.
- Model: **gpt-4o-mini**
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

### Fundamental Analyst
- Sources: SEC EDGAR, earnings transcripts, revenue/margin trends, FCF, debt, insider transactions, valuation multiples vs peers
- Hunts: Earnings beats not yet priced, insider buying clusters, undervalued vs sector
- Output: Fundamental score + key facts memo
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

### Technical Analyst
- Sources: Price/volume, MACD, RSI, 50/200-day MA, support/resistance, volume spikes
- Hunts: Breakout setups, divergences, accumulation patterns
- Output: Technical score + entry/exit zone
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

### Sentiment & News Analyst
- Sources: NewsAPI, Reddit (WSB, r/investing), Twitter/X financial accounts, analyst upgrades/downgrades, short interest, earnings call tone
- Hunts: Narrative shifts before price moves, extreme sentiment as contrarian signal, unusual social volume
- Output: Sentiment score + narrative risks/catalysts
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

### Macro Analyst
- Sources: FRED, earnings calendar, sector rotation signals, VIX, dollar index, yield curve
- Hunts: Macro tailwinds for specific sectors, rate-sensitive names, commodity-linked setups
- Output: Macro context memo — is the tide in or out
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

### Alpha Hunter ← key differentiator
- Proactively scans for opportunities retail misses:
  - Spin-offs and restructurings
  - Post-earnings drift setups
  - Small/mid-cap with zero analyst coverage
  - Dark pool unusual activity
  - Insider buying in quiet names
  - FDA/patent/contract award catalysts
  - Sector leaders in overlooked industries
- Sources: SEC EDGAR 8-K scanner, unusual options activity, government contract databases, biotech catalyst calendars
- Output: Daily ranked opportunity report
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

### Bull / Bear Researchers
- Bull: Builds strongest possible buy case from analyst memos
- Bear: Builds strongest possible case against, same data
- 2 rounds of structured debate → Debate Summary → CIO and CEO
- This is the core of the alpha edge — retail never stress-tests their own thesis
- Read `INVESTOR_PROFILE.md` before every decision. All recommendations must be consistent with Robert's profile, constraints, and current portfolio state.

---

## CEO Decision Memo Format

```
═══════════════════════════════════════════════
AXE CAPITAL — DECISION MEMO
═══════════════════════════════════════════════
DATE: [date]
TICKER: [symbol] | [company name]
ACTION: BUY | SELL | HOLD | PASS
CONVICTION: [1–10]
───────────────────────────────────────────────
THESIS
[2–3 sentences. What the market is missing. Why now.]

ENTRY ZONE:    $[X] – $[Y]
PROFIT TARGET: $[Z] ([X]% upside, [timeframe])
STOP-LOSS:     $[W] ([Y]% max loss)
POSITION SIZE: [X]% of portfolio
───────────────────────────────────────────────
SUPPORTING DATA
• Fundamental: [score] — [1-line]
• Technical:   [score] — [1-line]
• Sentiment:   [score] — [1-line]
• Macro:       [tailwind/headwind] — [1-line]
───────────────────────────────────────────────
BEAR CASE
• [point 1]
• [point 2]
• [why we proceed despite it]
───────────────────────────────────────────────
RISK GATE: [APPROVED / CONDITIONAL]
═══════════════════════════════════════════════
```

---

## Dashboard — What Robert Sees

Standalone React web app. Not Obsidian. Accessible over Tailscale.

**Panel 1 — Portfolio State**: Positions, entry price, current price, unrealized P&L, sector allocation heatmap, cash level.

**Panel 2 — Watchlist & Targets**: All monitored tickers. Distance to profit target and stop-loss. Color-coded: green (far) → yellow (approaching) → red (within 5%).

**Panel 3 — Alpha Opportunities**: Live feed from Alpha Hunter. Each card: ticker, opportunity type, one-line thesis, conviction, source.

**Panel 4 — Hot News**: Relevant news filtered and scored by Sentiment Analyst. Tagged: existing position vs. new opportunity. Time-stamped, source-linked.

**Panel 5 — Agent Status Board**: Real-time state of each agent. States: IDLE | SEARCHING | ANALYZING | REPORTING | DEBATING | BLOCKED. Last action timestamp + current task.

**Panel 6 — Internal Dialogue Viewer**: Full agent message threads. Bull vs. Bear debate transcript. CEO reasoning chain. Expandable per agent.

**Panel 7 — Decision Archive**: All past memos. Filterable by ticker, action, date, conviction. Outcome tracking: what happened vs. what was decided.

---

## Operating Rhythm

| Time | Event |
|---|---|
| 9:00 AM ET daily | Morning scan: overnight news, pre-market movers, open position checks, Alpha Hunter update |
| On-demand | Robert names ticker → full pipeline → decision memo |
| Every 30 min (market hours) | Open position monitoring vs. stop-loss thresholds |
| Sunday | Weekly portfolio review + CEO health memo |

---

## Technology Stack

| Layer | Choice |
|---|---|
| Agent LLMs | gpt-4o (CEO, CIO, CRO, Fundamental, Technical, Sentiment, Macro, Bull/Bear) / gpt-4o-mini (COO, Alpha Hunter summaries) |
| Agent runtime | OpenClaw |
| Backend | FastAPI (Python) |
| Dashboard | React + Tailwind |
| Prices | yfinance → Alpha Vantage (phase 2) |
| News | NewsAPI + RSS scraper |
| Social | Reddit PRAW + Twitter/X API |
| Filings | SEC EDGAR API (free) |
| Macro | FRED API (free) |
| Unusual activity | Unusual Whales API (phase 2) |
| Storage | PostgreSQL |
| Notifications | Telegram |
| Trade execution | Manual — Robert at IBKR |

---

## Implementation Plan

### Step 1 — Data Foundation (COO Agent)
*Nothing works without clean data. Build this first.*
- [ ] yfinance wrapper: price history, financials, earnings dates
- [ ] SEC EDGAR API: recent 8-K/10-K/13F pulls
- [ ] NewsAPI: filtered by ticker and sector keywords
- [ ] FRED API: key macro indicators (rates, CPI, VIX proxy)
- [ ] Reddit PRAW: WSB + r/investing scraper
- [ ] Data normalization: all outputs to structured JSON
- [ ] Freshness checker: flag stale data before analysis
- **Exit criteria**: Given a ticker, COO returns complete data bundle in <60s

### Step 2 — Single-Ticker Analysis Pipeline
*Wire analysts one by one. Test on a real ticker (AAPL or current holding).*
- [ ] Fundamental Analyst agent + prompt
- [ ] Technical Analyst agent + prompt
- [ ] Sentiment Analyst agent + prompt
- [ ] Macro Analyst agent + prompt
- [ ] Parallel execution: all 4 run simultaneously
- **Exit criteria**: 4 analyst memos generated in parallel in <3 minutes

### Step 3 — Debate + Decision Layer
- [ ] Bull Researcher prompt
- [ ] Bear Researcher prompt
- [ ] Debate facilitator: 2-round structured debate → summary
- [ ] CIO synthesis prompt → trade proposal
- [ ] CRO hard-rule enforcement → approval/block/condition
- [ ] CEO synthesis prompt → decision memo in standard format
- **Exit criteria**: Ticker in → decision memo out, end to end

### Step 4 — Alpha Hunter Agent
*The proactive search layer. This is what separates this from reactive tools.*
- [ ] SEC 8-K scanner: unusual filings (asset sales, leadership changes, contract awards)
- [ ] Insider buying scanner: clusters in last 30 days
- [ ] Earnings surprise scanner: beats/misses with delayed price reaction
- [ ] Spin-off/restructuring tracker: recent corporate actions
- [ ] Opportunity ranker: scores and ranks findings, outputs top 5 daily
- **Exit criteria**: Daily alpha report with ranked, thesis-backed candidates

### Step 5 — Portfolio Tracking
- [ ] IBKR CSV import parser
- [ ] Portfolio state model: positions, entry, P&L, sector allocation
- [ ] Target/stop distance calculator with alert thresholds
- [ ] Performance tracker: return vs. SPY
- **Exit criteria**: Accurate portfolio state from CSV drops

### Step 6 — Dashboard Frontend
- [ ] React app scaffold + routing
- [ ] Portfolio State panel
- [ ] Watchlist & Targets with color-coded urgency
- [ ] Alpha Opportunities live feed
- [ ] Hot News feed (filtered + scored)
- [ ] Agent Status Board (real-time states)
- [ ] Internal Dialogue Viewer
- [ ] Decision Archive with outcome tracking
- [ ] Monthly PDF Report — generated 1st of each month via cron, delivered to Telegram as PDF. One page per open position (scores, price chart, thesis health, P&L, stop distance). Portfolio summary page with SPY comparison, hishtalmut status, and Alpha Hunter top 5 for next month. Tech: Python with reportlab or weasyprint.
- [ ] Tailscale-accessible deployment
- **Exit criteria**: Dashboard live, all panels populated with real data

### Step 7 — Automation & Scheduling
- [ ] Morning scan cron (9:00 AM ET)
- [ ] Alpha Hunter daily overnight scan
- [ ] Position monitor (every 30 min, market hours)
- [ ] Weekly review auto-trigger (Sunday)
- [ ] OpenClaw heartbeat integration
- [ ] Telegram alerts for: stop-loss proximity, new alpha opportunity, decision memo ready
- **Exit criteria**: System runs without Robert touching it. He wakes up to a brief.

### Step 8 — Hardening & Tuning
- [ ] Prompt refinement based on real decision quality
- [ ] Back-test mode: run pipeline on historical dates
- [ ] Data source upgrades: Alpha Vantage, Polygon.io, Unusual Whales
- [ ] Graceful degradation: partial memos flagged when data missing
- [ ] IBKR API direct connection (replaces CSV drops)
- **Exit criteria**: Production-grade. Reliable enough to trust daily.

---

## Devil's Advocate Audit

**Q: Reddit and social media is mostly noise.**  
A: True for individual posts. Signal lives in anomalies — unusual volume spikes, sentiment extremes as contrarian indicators, coordinated narrative shifts. The Sentiment Analyst is tuned for anomaly detection, not following the crowd.

**Q: gpt-4o will sound confident even when it's guessing.**  
A: CEO only sees structured, data-cited memos. CRO blocks rule violations before CEO processes them. Robert reviews every memo. Conviction scores (1-10) plus mandatory bear case documentation calibrate confidence explicitly.

**Q: This is a lot of infra for one person's portfolio.**  
A: The Alpha Hunter alone justifies it. Finding one overlooked spin-off, one insider-buying cluster, one post-earnings drift play per quarter that retail misses — that's the ROI. The infrastructure cost is time, not money (all free-tier APIs in Phase 1).

**Q: Two agents disagree and CEO picks wrong — what then?**  
A: It's in the memo. Bear case is documented. Robert tracks outcomes against decisions in the archive. Over time, patterns of failure tell us which agent prompts need tuning.

**Q: API rate limits and costs.**  
A: Phase 1 is entirely free tiers: yfinance, NewsAPI free, PRAW, FRED, SEC EDGAR. Cost only grows when volume demands it. Phase 2 upgrades are optional and budgeted per data source.
