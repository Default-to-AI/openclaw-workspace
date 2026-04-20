# Axe Capital — Mission Log

Running record of what was built, why, and what changed. Newest entries at top.

---

## 2026-04-20 — Session: Vault Task Blitz

**Operator:** Claude (Sonnet 4.6)  
**Session goal:** Work through open tasks from the vault task list, fix bugs, log everything.

---

### TASK-01 — Weekly review artifact not updating in dashboard
**Status:** ✅ Fixed  
**File:** `step5-portfolio-tracking/axe_portfolio/tracker.py`  
**Problem:** `write_weekly_review()` wrote only to `step5-portfolio-tracking/reports/weekly-review-latest.json`. The dashboard reads from `step6-dashboard/public/weekly-review-latest.json`. These were two different files. Every run left the public copy stale (e.g. showing April 12 data while portfolio.json showed today).  
**Fix:** Added a second write inside `run_portfolio_review()` that copies the weekly review JSON to `DASHBOARD_JSON_PATH.parent / "weekly-review-latest.json"` after the first write. Surgical — no logic change, just dual-write.  
**Test:** Ran `axe-portfolio-review`, confirmed `step6-dashboard/public/weekly-review-latest.json` now matches today's date and all 14 positions (including both accounts).  
**Impact:** Weekly Review panel now always shows current data.

---

### TASK-02 — SPY comparison values rendered as percentages
**Status:** ✅ Fixed  
**File:** `step6-dashboard/src/components/WeeklyReviewPanel.jsx`  
**Problem:** The `spy_comparison` object contains both dollar amounts (`portfolio_cost_basis`, `portfolio_market_value`) and percentages (`portfolio_return_pct`, `spy_return_pct_same_window`, `relative_alpha_pct`). The render loop applied `%` to all values, making `portfolio_cost_basis: 110905.11` display as `+110905.11%`.  
**Fix:** Keys ending in `_pct` get formatted as signed percentages. Keys containing `cost_basis` or `market_value` get formatted as USD. Human-readable key labels replace raw underscore-separated keys.  
**Impact:** SPY comparison section now correctly shows `$110,905` and `$120,454` for cost/market, and `+8.61%` for return.

---

### TASK-03 — Portfolio P&L: plus sign before dollar sign (+$)
**Status:** ✅ Fixed  
**File:** `step6-dashboard/src/components/PortfolioPanel.jsx`  
**Problem:** Positive unrealized P&L showed as `+$9,549` (plus before dollar) and `+$750` in the table. Negative values were shown without minus (`$52`) due to `Math.abs` in `fmtUSD`. Both are confusing.  
**Fix:** Replaced ad-hoc `sign() + fmtUSD()` calls with a single `fmtSignedUSD(n)` helper that produces `+$X,XXX`, `-$X,XXX`, or `$X,XXX` correctly for all sign states.  
**Impact:** P&L values now display as `+$9,549` or `-$52` consistently.

---

### TASK-04 — Alert status legend not visible / status column
**Status:** ✅ Fixed  
**File:** `step6-dashboard/src/components/PortfolioPanel.jsx`  
**Problem:** The legend (colored dots + RED/YELLOW/GREEN counts) was rendered in the header but only when `data?.summary` was truthy. On mobile the header wrapped and the legend was invisible. The alert status column in the table had no tooltip explaining criteria.  
**Fix:** Added a legend footer below the position table explaining thresholds (RED = dist < 5%, YELLOW = dist < 10%, GREEN = safe). Header legend stays; footer adds context.  
**Impact:** Users can now see at a glance what each alert level means.

---

### TASK-05 — Vault task checklist sync
**Status:** ✅ Fixed  
**File:** `/home/tiger/.openclaw/workspace/obsidian-vault/Axe_Capital_Tasks.md`  
**Problem:** Several tasks completed in this and previous sessions were not marked done in the vault.  
**Marked done:**
- Wire Flex fallback into tracker.py ✅
- Update PortfolioPanel.jsx dynamic source label ✅

---

### Earlier session (2026-04-20 morning) — Flex Query implementation complete
All 4 tasks from `plans/2026-04-20-flex-query-implementation.md` committed:
- `flex.py` connector
- Error-case tests (5 total)
- Flex fallback in tracker.py + data_source in portfolio.json
- PortfolioPanel.jsx dynamic source label

Plus follow-up session fixes:
- Aggregate duplicate symbols across accounts
- USD-only cash filtering
- Warning logs on silent fallback
- data_source in trace events
- axe-dev.sh portfolio preflight section
