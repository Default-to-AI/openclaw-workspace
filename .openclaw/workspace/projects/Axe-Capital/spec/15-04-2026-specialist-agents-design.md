# Specialist Analyst Agents — Design Spec

**Date:** 2026-04-15
**Status:** Approved
**Type:** Implementation Design

---

## 1. Goal

Implement 3 specialist analyst agents (Fundamental, Technical, Macro) that run **before** the Bull/Bear debate, feeding their reports into the decision pipeline.

---

## 2. Architecture

### New Packages

| Package | Purpose |
|---------|---------|
| `step8-fundamental/` | Fundamental Analyst agent |
| `step9-technical/` | Technical Analyst agent |
| `step10-macro/` | Macro Strategist agent |

### Pipeline Flow

```
ticker 
  → step8 (Fundamental) → fundamental_report.json + .md
  → step9 (Technical) → technical_report.json + .md
  → step10 (Macro) → macro_report.json + .md
        ↓
    step3 (Debate) — reads 3 reports, injects into Bull/Bear prompts
        ↓
      CRO → CEO → decision memo
```

---

## 3. Each Agent Specification

### 3.1 Fundamental Analyst (step8-fundamental)

**Purpose:** Business quality, earnings, balance sheet, valuation

**Data Sources (free):**
- yfinance (earnings, financials, metrics)
- SEC EDGAR (10-K, 10-Q filings)
- News RSS (earnings-related)

**Outputs:**
- `step6-dashboard/public/analyst-reports/<ticker>-fundamental-<date>.json`
- `step6-dashboard/public/analyst-reports/<ticker>-fundamental-<date>.md`

**JSON Schema:**
```json
{
  "generated_at": "2026-04-15T12:00:00Z",
  "ticker": "MSFT",
  "agent": "fundamental",
  "summary": "2-paragraph thesis",
  "key_findings": ["finding1", "finding2"],
  "data_sources": ["yfinance", "sec-edgar"],
  "confidence": 7,
  "report": "full detailed report..."
}
```

**MD Report Format:**
- Title with ticker and date
- Executive Summary (2-3 sentences)
- Business Overview
- Earnings Analysis (with metrics table)
- Valuation (DCF, comparable, etc.)
- Risks
- Confidence Score
- Sources

---

### 3.2 Technical Analyst (step9-technical)

**Purpose:** Market structure, entry/exit levels, trend, support/resistance

**Data Sources (free):**
- yfinance (price, volume, OHLC)
- Yahoo Finance (charts)

**Outputs:**
- `step6-dashboard/public/analyst-reports/<ticker>-technical-<date>.json`
- `step6-dashboard/public/analyst-reports/<ticker>-technical-<date>.md`

**JSON Schema:** Same as Fundamental, with technical-specific fields

**MD Report Format:**
- Title with ticker and date
- Executive Summary
- Price Action (trend analysis)
- Key Levels (support, resistance, invalidation)
- Technical Indicators (RSI, MACD, moving averages)
- Entry/Exit Recommendations
- Risk Factors
- Confidence Score

---

### 3.3 Macro Strategist (step10-macro)

**Purpose:** Rates, USD, liquidity, sector rotation, regime

**Data Sources (free):**
- FRED (federal funds rate, inflation, GDP)
- Yahoo Finance (USD index, commodities, sector ETFs)

**Outputs:**
- `step6-dashboard/public/analyst-reports/<ticker>-macro-<date>.json`
- `step6-dashboard/public/analyst-reports/<ticker>-macro-<date>.md`

**JSON Schema:** Same as others, macro-specific fields

**MD Report Format:**
- Title with ticker and date
- Executive Summary
- Macro Context (rates, USD, inflation)
- Sector Rotation Analysis
- Liquidity Conditions
- Regime Assessment (bull/bear/neutral)
- Impact on Ticker
- Confidence Score

---

## 4. Shared Components

All 3 agents use:
- **axe_core** for trace and paths
- **GPT-4o-mini** for LLM analysis
- **Shared report template** (common MD layout)
- **Output directory:** `step6-dashboard/public/analyst-reports/`

---

## 5. Integration with step3 (Debate)

The debate CLI (`axe-decision TICKER`) will:
1. Check for existing analyst reports (within 24h)
2. If missing, run step8 → step9 → step10
3. Read all 3 JSON reports
4. Inject into Bull/Bear prompts:

```
Bull system: "You have fundamental_report, technical_report, macro_report from specialist analysts. Build the strongest BUY case..."
```

---

## 6. Orchestration

`axe run decision TICKER` becomes:
```bash
axe run fundamental TICKER    # optional, skips if fresh
axe run technical TICKER       # optional, skips if fresh
axe run macro TICKER           # optional, skips if fresh
axe run debate TICKER          # uses reports if available
```

---

## 7. Decision Flow (Who Decides)

```
Bull Researcher → Buy case (uses analyst reports)
Bear Researcher → Sell case (uses analyst reports)
     ↓
CRO (Chief Risk Officer) → Risk gate (can BLOCK)
     ↓
CEO (Final Decision) → Synthesizes all, outputs action
```

**CEO makes final decision.** CRO can veto. Robert executes manually.

---

## 8. Files Created

Each agent creates:
- `axe_<agent>/__init__.py`
- `axe_<agent>/cli.py` (main entry)
- `axe_<agent>/report generator.py` (LLM + formatting)
- `axe_<agent>/templates/` (MD report template)
- `pyproject.toml`

---

## 9. Acceptance Criteria

- [ ] step8-fundamental produces JSON + MD report
- [ ] step9-technical produces JSON + MD report  
- [ ] step10-macro produces JSON + MD report
- [ ] step3-debate reads analyst reports and injects into prompts
- [ ] All trace to `traces/` via axe_core
- [ ] Reports accessible in `public/analyst-reports/`
- [ ] MD reports are beautiful and human-readable
- [ ] `axe run decision TICKER` works end-to-end

---

*Last updated: 2026-04-15*