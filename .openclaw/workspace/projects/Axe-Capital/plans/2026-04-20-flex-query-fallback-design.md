# IBKR Flex Query Fallback — Design Spec

**Date:** 2026-04-20
**Status:** Approved

---

## Goal

When TWS is unreachable, fetch live portfolio positions and cash from IBKR's Flex Web Service (HTTP API) instead of failing. Flex Query is T+1 end-of-day data from IBKR's servers — no local gateway required.

---

## Fallback Order

```
_resolve_portfolio_input()
  └── try fetch_ibkr_portfolio()        ← live TWS socket (unchanged)
        on failure or empty rows:
          └── try fetch_flex_portfolio() ← new: IBKR Flex HTTP
                on failure:
                  └── raise              ← no further fallback
```

CSV fallback removed. If both live and Flex fail, the error surfaces to the caller.

---

## Flex Web Service Protocol

Two-step HTTP flow. Both steps are plain GETs over HTTPS.

**Step 1 — Request report:**
```
GET https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest
    ?t=<token>&q=<queryId>&v=3
```
Returns XML. On success: `<Status>Success</Status>` and a `<ReferenceCode>`.  
On error: `<ErrorCode>` and `<ErrorMessage>`.

**Step 2 — Fetch statement (poll with retries):**
```
GET https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement
    ?q=<referenceCode>&t=<token>&v=3
```
IBKR may return `Statement generation in progress` for up to ~30s. Poll with 3s sleep between attempts (max 10 retries). On success: full XML statement.

---

## Configuration

Loaded from `Axe-Capital/.env` via `FlexQueryConfig.from_env()`:

```
AXE_IBKR_FLEX_TOKEN=<token>       # account-wide Flex token
AXE_IBKR_FLEX_QUERY_ID=<id>       # numeric ID of the specific query
```

If either is missing, `fetch_flex_portfolio()` raises immediately with a setup message — no network call made.

---

## XML Fields Parsed

**Positions** — from `<OpenPosition>` elements:

| XML attribute | Maps to |
|--------------|---------|
| `symbol` | `symbol` |
| `position` | `position` (shares) |
| `markPrice` | `last` |
| `costBasisPrice` | `avg_price` |
| `costBasisMoney` | `cost_basis` |
| `fifoPnlUnrealized` | `unrealized_pl` |

Derived fields computed the same way as `ibkr.py`:
- `market_value = position × last`
- `unrealized_pl_pct = (unrealized_pl / cost_basis) × 100`
- `change_pct`, `pe`, `eps_current` → `None` (not available from Flex)

Skip rows where `secType` is `CASH` or `BAG` (same filter as live path).

**Cash** — from `<CashReportCurrency currency="BASE">`:
- Field: `endingCash`
- BASE currency = USD equivalent total across all currencies

---

## Return Type

`fetch_flex_portfolio() -> tuple[list[dict], float]`

Identical to `fetch_ibkr_portfolio()`. `tracker.py` cannot distinguish the source.

---

## Error Handling

| Condition | Behaviour |
|-----------|-----------|
| Token or Query ID missing from env | Raise `RuntimeError` with setup instructions |
| IBKR returns error code in XML | Raise `RuntimeError` with IBKR's error message |
| Step 2 still pending after 10 retries (30s) | Raise `TimeoutError` |
| Zero positions returned | Raise `RuntimeError("Flex Query returned no positions")` |
| Network error (DNS, SSL, connection refused) | Re-raise as-is |

---

## Files

| File | Action |
|------|--------|
| `step5-portfolio-tracking/axe_portfolio/flex.py` | Create — full Flex connector |
| `step5-portfolio-tracking/tests/test_flex.py` | Create — unit tests with XML fixtures |
| `step5-portfolio-tracking/axe_portfolio/tracker.py` | Modify — add Flex fallback in `_resolve_portfolio_input()` |
| `.env` | Already updated with token + query ID |

---

## Tests

**`test_flex.py`** covers:
1. Happy path — static XML with 2 positions + cash parses to correct `(rows, cash)` shape
2. Missing env vars — raises before any HTTP call
3. IBKR error code in Step 1 response — raises with IBKR message
4. Step 2 still pending after max retries — raises `TimeoutError`
5. Zero positions in response — raises

**`tracker.py` integration test** (added to `test_ibkr.py` or new file):
- Monkeypatch `fetch_ibkr_portfolio` to raise `ConnectionRefusedError`
- Monkeypatch `fetch_flex_portfolio` to return a known `(rows, cash)`
- Assert `_resolve_portfolio_input()` returns `kind="flex"` with those rows

---

## Spec Self-Review

- No TBDs or placeholders
- Return type is consistent throughout
- Error table covers all reachable failure paths
- `kind="flex"` needs to be added to `PortfolioInput` dataclass in `tracker.py` — noted
- Scope is a single connector file + small tracker change — no decomposition needed
