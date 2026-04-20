# Flex Query Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an IBKR Flex Query fallback so the portfolio tracker can fetch T+1 position data from IBKR's HTTP API when TWS is unreachable, and display the data source in the dashboard.

**Architecture:** Three isolated changes wired together. A new `flex.py` module handles all HTTP/XML logic. `tracker.py` inserts Flex as the fallback tier between the live IBKR path and the error surface. `PortfolioPanel.jsx` reads `data_source` from `portfolio.json` to show "IBKR live" or "Flex Query (T+1)". No shared state; each file has one clear job.

**Tech Stack:** Python 3.12, `requests` 2.33.1, `xml.etree.ElementTree`, pytest, React/JSX

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `step5-portfolio-tracking/axe_portfolio/flex.py` | Create | Full Flex HTTP connector — config, two-step fetch, XML parse |
| `step5-portfolio-tracking/tests/test_flex.py` | Create | Unit tests using static XML fixtures (no network calls) |
| `step5-portfolio-tracking/axe_portfolio/tracker.py` | Modify | Flex fallback in `_resolve_portfolio_input()`; `data_source` in `build_dashboard_json()` and `run_portfolio_review()` |
| `step6-dashboard/src/components/PortfolioPanel.jsx` | Modify | Replace hardcoded "IBKR snapshot" with dynamic source label |

---

## Task 1: Create `flex.py` — Happy Path

**Files:**
- Create: `step5-portfolio-tracking/axe_portfolio/flex.py`
- Create: `step5-portfolio-tracking/tests/test_flex.py` (happy path test only)

- [ ] **Step 1.1: Write the failing happy-path test**

Create `step5-portfolio-tracking/tests/test_flex.py`:

```python
from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest

from axe_portfolio.flex import fetch_flex_portfolio, FlexQueryConfig

SEND_SUCCESS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexStatementResponse timestamp="20260420;123000">
  <Status>Success</Status>
  <ReferenceCode>12345678</ReferenceCode>
  <Url>https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement</Url>
</FlexStatementResponse>"""

STATEMENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexQueryResponse queryName="AxePortfolio" type="AF">
  <FlexStatements count="1">
    <FlexStatement accountId="U123456" fromDate="20260419" toDate="20260419">
      <OpenPositions>
        <OpenPosition accountId="U123456" acctAlias="" model="" currency="USD"
          assetCategory="STK" symbol="TSLA" description="TESLA INC"
          conid="76792991" secType="STK" listingExchange="NASDAQ"
          position="50" markPrice="170.00" positionValue="8500.00"
          openPrice="155.00" costBasisPrice="155.00" costBasisMoney="7750.00"
          percentOfNAV="10.5" fifoPnlUnrealized="750.00"
          side="Long" levelOfDetail="SUMMARY" openDateTime="" holdingPeriodDateTime=""
          currency2="" fxRateToBase="1" />
        <OpenPosition accountId="U123456" acctAlias="" model="" currency="USD"
          assetCategory="STK" symbol="MSFT" description="MICROSOFT CORP"
          conid="272093" secType="STK" listingExchange="NASDAQ"
          position="30" markPrice="420.00" positionValue="12600.00"
          openPrice="400.00" costBasisPrice="400.00" costBasisMoney="12000.00"
          percentOfNAV="15.2" fifoPnlUnrealized="600.00"
          side="Long" levelOfDetail="SUMMARY" openDateTime="" holdingPeriodDateTime=""
          currency2="" fxRateToBase="1" />
        <OpenPosition accountId="U123456" acctAlias="" model="" currency="USD"
          assetCategory="CASH" symbol="USD.EUR" description="USD.EUR"
          conid="12087792" secType="CASH" listingExchange=""
          position="1000" markPrice="0.93" positionValue="930.00"
          openPrice="0.93" costBasisPrice="0.93" costBasisMoney="930.00"
          percentOfNAV="1.1" fifoPnlUnrealized="0.00"
          side="Long" levelOfDetail="SUMMARY" openDateTime="" holdingPeriodDateTime=""
          currency2="" fxRateToBase="1" />
      </OpenPositions>
      <CashReport>
        <CashReportCurrency accountId="U123456" currency="BASE"
          fromDate="20260419" toDate="20260419"
          startingCash="9000.00" endingCash="9253.00"
          endingCashPaxos="" />
        <CashReportCurrency accountId="U123456" currency="USD"
          fromDate="20260419" toDate="20260419"
          startingCash="9000.00" endingCash="9253.00"
          endingCashPaxos="" />
      </CashReport>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>"""


def _mock_responses(send_xml: str, statement_xml: str):
    """Return a side_effect list: first call returns send_xml, second returns statement_xml."""
    send_resp = MagicMock()
    send_resp.raise_for_status.return_value = None
    send_resp.text = send_xml

    stmt_resp = MagicMock()
    stmt_resp.raise_for_status.return_value = None
    stmt_resp.text = statement_xml

    return [send_resp, stmt_resp]


def test_happy_path():
    config = FlexQueryConfig(token="tok123", query_id="987654")
    with patch("axe_portfolio.flex.requests.get", side_effect=_mock_responses(SEND_SUCCESS_XML, STATEMENT_XML)):
        rows, cash = fetch_flex_portfolio(config)

    assert cash == pytest.approx(9253.0)
    assert len(rows) == 2  # CASH row filtered out

    symbols = {r["symbol"] for r in rows}
    assert symbols == {"TSLA", "MSFT"}

    tsla = next(r for r in rows if r["symbol"] == "TSLA")
    assert tsla["position"] == 50.0
    assert tsla["last"] == pytest.approx(170.00)
    assert tsla["avg_price"] == pytest.approx(155.00)
    assert tsla["cost_basis"] == pytest.approx(7750.00)
    assert tsla["unrealized_pl"] == pytest.approx(750.00)
    assert tsla["market_value"] == pytest.approx(8500.00)
    assert tsla["change_pct"] is None
    assert tsla["pe"] is None
    assert tsla["eps_current"] is None
```

- [ ] **Step 1.2: Run test to confirm it fails**

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
source /home/tiger/.openclaw/workspace/projects/Axe-Capital/.venv/bin/activate
pytest tests/test_flex.py::test_happy_path -v
```

Expected: `ModuleNotFoundError: No module named 'axe_portfolio.flex'`

- [ ] **Step 1.3: Create `flex.py`**

Create `step5-portfolio-tracking/axe_portfolio/flex.py`:

```python
from __future__ import annotations

import os
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import requests

_SEND_URL = "https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"
_GET_URL = "https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement"
_MAX_RETRIES = 10
_RETRY_SLEEP = 3.0
_SKIP_ASSET_CATEGORIES = {"CASH", "BAG", "FXCFD"}


@dataclass
class FlexQueryConfig:
    token: str
    query_id: str
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> "FlexQueryConfig":
        token = os.getenv("AXE_IBKR_FLEX_TOKEN", "").strip()
        query_id = os.getenv("AXE_IBKR_FLEX_QUERY_ID", "").strip()
        if not token or not query_id:
            raise RuntimeError(
                "Flex Query requires AXE_IBKR_FLEX_TOKEN and AXE_IBKR_FLEX_QUERY_ID in .env. "
                "Set them in IBKR Account Management → Reports → Flex Queries."
            )
        return cls(token=token, query_id=query_id)


def _parse_send_response(xml_text: str) -> str:
    root = ET.fromstring(xml_text)
    status = root.findtext("Status", "")
    if status != "Success":
        code = root.findtext("ErrorCode", "unknown")
        msg = root.findtext("ErrorMessage", "no message")
        raise RuntimeError(f"Flex Query SendRequest failed (code {code}): {msg}")
    ref = root.findtext("ReferenceCode", "")
    if not ref:
        raise RuntimeError("Flex Query SendRequest returned Success but no ReferenceCode")
    return ref


def _request_statement(config: FlexQueryConfig) -> str:
    resp = requests.get(
        _SEND_URL,
        params={"t": config.token, "q": config.query_id, "v": "3"},
        timeout=config.timeout,
    )
    resp.raise_for_status()
    return _parse_send_response(resp.text)


def _fetch_statement(ref_code: str, config: FlexQueryConfig) -> str:
    for attempt in range(_MAX_RETRIES):
        resp = requests.get(
            _GET_URL,
            params={"q": ref_code, "t": config.token, "v": "3"},
            timeout=config.timeout,
        )
        resp.raise_for_status()
        text = resp.text
        if "Statement generation in progress" in text:
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_SLEEP)
                continue
            raise TimeoutError(
                f"Flex Query statement still pending after {_MAX_RETRIES} retries ({_MAX_RETRIES * _RETRY_SLEEP:.0f}s)"
            )
        return text
    raise TimeoutError(f"Flex Query statement still pending after {_MAX_RETRIES} retries")


def _parse_statement(xml_text: str) -> tuple[list[dict], float]:
    root = ET.fromstring(xml_text)

    rows: list[dict] = []
    for pos in root.iter("OpenPosition"):
        if pos.attrib.get("assetCategory", "") in _SKIP_ASSET_CATEGORIES:
            continue
        symbol = pos.attrib.get("symbol", "")
        position = float(pos.attrib.get("position", 0))
        last = float(pos.attrib.get("markPrice", 0))
        avg_price = float(pos.attrib.get("costBasisPrice", 0))
        cost_basis = float(pos.attrib.get("costBasisMoney", 0))
        unrealized_pl = float(pos.attrib.get("fifoPnlUnrealized", 0))
        market_value = round(position * last, 2)
        unrealized_pl_pct = round((unrealized_pl / cost_basis) * 100, 2) if cost_basis else 0.0
        rows.append({
            "symbol": symbol,
            "position": position,
            "last": last,
            "avg_price": avg_price,
            "cost_basis": cost_basis,
            "unrealized_pl": unrealized_pl,
            "unrealized_pl_pct": unrealized_pl_pct,
            "market_value": market_value,
            "change_pct": None,
            "pe": None,
            "eps_current": None,
        })

    cash = 0.0
    for cash_el in root.iter("CashReportCurrency"):
        if cash_el.attrib.get("currency") == "BASE":
            cash = float(cash_el.attrib.get("endingCash", 0))
            break

    return rows, cash


def fetch_flex_portfolio(config: FlexQueryConfig | None = None) -> tuple[list[dict], float]:
    if config is None:
        config = FlexQueryConfig.from_env()
    ref_code = _request_statement(config)
    xml_text = _fetch_statement(ref_code, config)
    rows, cash = _parse_statement(xml_text)
    if not rows:
        raise RuntimeError("Flex Query returned no positions")
    return rows, cash
```

- [ ] **Step 1.4: Run test to confirm it passes**

```bash
pytest tests/test_flex.py::test_happy_path -v
```

Expected: `PASSED`

- [ ] **Step 1.5: Commit**

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital
git add step5-portfolio-tracking/axe_portfolio/flex.py step5-portfolio-tracking/tests/test_flex.py
git commit -m "feat: add flex.py connector and happy-path test"
```

---

## Task 2: Add Error-Case Tests for `flex.py`

**Files:**
- Modify: `step5-portfolio-tracking/tests/test_flex.py` (add 4 more test functions)

- [ ] **Step 2.1: Add the four error-case tests**

Append to `step5-portfolio-tracking/tests/test_flex.py`:

```python
SEND_ERROR_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexStatementResponse timestamp="20260420;123000">
  <Status>Fail</Status>
  <ErrorCode>1012</ErrorCode>
  <ErrorMessage>Token has expired.</ErrorMessage>
</FlexStatementResponse>"""

PENDING_XML = "Statement generation in progress"


def test_missing_env_vars_raises(monkeypatch):
    monkeypatch.delenv("AXE_IBKR_FLEX_TOKEN", raising=False)
    monkeypatch.delenv("AXE_IBKR_FLEX_QUERY_ID", raising=False)
    with pytest.raises(RuntimeError, match="AXE_IBKR_FLEX_TOKEN"):
        fetch_flex_portfolio()


def test_ibkr_error_code_raises():
    config = FlexQueryConfig(token="tok", query_id="123")
    send_resp = MagicMock()
    send_resp.raise_for_status.return_value = None
    send_resp.text = SEND_ERROR_XML
    with patch("axe_portfolio.flex.requests.get", return_value=send_resp):
        with pytest.raises(RuntimeError, match="Token has expired"):
            fetch_flex_portfolio(config)


def test_timeout_after_max_retries():
    config = FlexQueryConfig(token="tok", query_id="123")
    send_resp = MagicMock()
    send_resp.raise_for_status.return_value = None
    send_resp.text = SEND_SUCCESS_XML

    pending_resp = MagicMock()
    pending_resp.raise_for_status.return_value = None
    pending_resp.text = PENDING_XML

    side_effects = [send_resp] + [pending_resp] * 10
    with patch("axe_portfolio.flex.requests.get", side_effect=side_effects):
        with patch("axe_portfolio.flex.time.sleep"):  # skip real sleeps
            with pytest.raises(TimeoutError):
                fetch_flex_portfolio(config)


EMPTY_STATEMENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexQueryResponse queryName="AxePortfolio" type="AF">
  <FlexStatements count="1">
    <FlexStatement accountId="U123456" fromDate="20260419" toDate="20260419">
      <OpenPositions />
      <CashReport>
        <CashReportCurrency accountId="U123456" currency="BASE"
          fromDate="20260419" toDate="20260419"
          startingCash="9000.00" endingCash="9253.00" />
      </CashReport>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>"""


def test_empty_positions_raises():
    config = FlexQueryConfig(token="tok", query_id="123")
    with patch("axe_portfolio.flex.requests.get", side_effect=_mock_responses(SEND_SUCCESS_XML, EMPTY_STATEMENT_XML)):
        with pytest.raises(RuntimeError, match="no positions"):
            fetch_flex_portfolio(config)
```

- [ ] **Step 2.2: Run all flex tests**

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest tests/test_flex.py -v
```

Expected: `5 passed`

- [ ] **Step 2.3: Commit**

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital
git add step5-portfolio-tracking/tests/test_flex.py
git commit -m "test: add flex.py error-case tests (missing config, IBKR error, timeout, empty)"
```

---

## Task 3: Wire Flex Fallback into `tracker.py`

**Files:**
- Modify: `step5-portfolio-tracking/axe_portfolio/tracker.py` (3 locations)

The three changes:
1. `_resolve_portfolio_input()` — add Flex as fallback after IBKR fails
2. `build_dashboard_json()` — accept `data_source` param and write it to the returned dict
3. `run_portfolio_review()` — pass `portfolio_input.kind` as `data_source`

- [ ] **Step 3.1: Write the integration test**

Create `step5-portfolio-tracking/tests/test_flex_fallback.py`:

```python
from __future__ import annotations
from unittest.mock import patch
import pytest

from axe_portfolio.tracker import _resolve_portfolio_input


FAKE_ROWS = [
    {
        "symbol": "TSLA",
        "position": 50.0,
        "last": 170.0,
        "change_pct": None,
        "avg_price": 155.0,
        "cost_basis": 7750.0,
        "market_value": 8500.0,
        "unrealized_pl": 750.0,
        "unrealized_pl_pct": 9.68,
        "pe": None,
        "eps_current": None,
    }
]
FAKE_CASH = 9253.0


def test_flex_fallback_when_ibkr_fails(monkeypatch):
    monkeypatch.setenv("AXE_PORTFOLIO_SOURCE", "auto")
    with patch("axe_portfolio.tracker.fetch_ibkr_portfolio", side_effect=ConnectionRefusedError("TWS offline")):
        with patch("axe_portfolio.tracker.fetch_flex_portfolio", return_value=(FAKE_ROWS, FAKE_CASH)):
            result = _resolve_portfolio_input()
    assert result.kind == "flex"
    assert result.cash == FAKE_CASH
    assert result.rows[0]["symbol"] == "TSLA"
```

- [ ] **Step 3.2: Run test to confirm it fails**

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest tests/test_flex_fallback.py -v
```

Expected: `FAILED` — `fetch_flex_portfolio` not imported in tracker, no Flex fallback logic yet.

- [ ] **Step 3.3: Add Flex import and fallback in `_resolve_portfolio_input()`**

In `step5-portfolio-tracking/axe_portfolio/tracker.py`, find the import for `fetch_ibkr_portfolio` and add the Flex import alongside it. Then modify `_resolve_portfolio_input()` at line 368.

**Import addition** — find the existing ibkr import line (search for `from axe_portfolio.ibkr`) and add:
```python
from axe_portfolio.flex import fetch_flex_portfolio
```

**`_resolve_portfolio_input()` change** — replace the current fallthrough-to-CSV block (lines 385–410+). The current code after the IBKR try/except block falls through to `_resolve_normalized_source()`. Replace so that the Flex fetch happens before the CSV fallback:

Find this block (starts at line 385):
```python
    normalized_source = _resolve_normalized_source()
    if normalized_source is not None:
        return PortfolioInput(
            kind="normalized",
            path=normalized_source,
            rows=_load_normalized_portfolio_csv(normalized_source),
            cash=_read_cash_from_existing_dashboard(),
        )
```

Insert the Flex fallback **before** that block (after the IBKR try/except closes, before the CSV resolution):

```python
    if source in {"ibkr", "auto"}:
        try:
            rows, cash = fetch_flex_portfolio()
        except Exception:
            if source == "ibkr":
                raise
        else:
            return PortfolioInput(kind="flex", path=Path("flex://ibkr"), rows=rows, cash=cash)
```

After the edit, the relevant section of `_resolve_portfolio_input()` should read:

```python
def _resolve_portfolio_input() -> PortfolioInput:
    source = os.getenv("AXE_PORTFOLIO_SOURCE", "ibkr").strip().lower()
    if source not in {"csv", "ibkr", "auto"}:
        raise ValueError("AXE_PORTFOLIO_SOURCE must be one of: csv, ibkr, auto")

    if source in {"ibkr", "auto"}:
        try:
            rows, cash = fetch_ibkr_portfolio()
        except Exception:
            if source == "ibkr":
                raise
        else:
            if rows:
                return PortfolioInput(kind="ibkr", path=Path("ibkr://live"), rows=rows, cash=cash)
            if source == "ibkr":
                raise RuntimeError("IBKR connection succeeded, but no portfolio positions were returned.")

    if source in {"ibkr", "auto"}:
        try:
            rows, cash = fetch_flex_portfolio()
        except Exception:
            if source == "ibkr":
                raise
        else:
            return PortfolioInput(kind="flex", path=Path("flex://ibkr"), rows=rows, cash=cash)

    normalized_source = _resolve_normalized_source()
    # ... rest unchanged
```

- [ ] **Step 3.4: Run fallback test to confirm it passes**

```bash
pytest tests/test_flex_fallback.py -v
```

Expected: `PASSED`

- [ ] **Step 3.5: Add `data_source` to `build_dashboard_json()`**

In `tracker.py` at line 562, modify the function signature and return dict:

Change the function signature from:
```python
def build_dashboard_json(
    position_table: list[dict[str, Any]],
    unified_sector_allocation: list[dict[str, Any]],
    hishtalmut_status: dict[str, Any],
    review_date: str,
    cash: float,
) -> dict[str, Any]:
```

To:
```python
def build_dashboard_json(
    position_table: list[dict[str, Any]],
    unified_sector_allocation: list[dict[str, Any]],
    hishtalmut_status: dict[str, Any],
    review_date: str,
    cash: float,
    data_source: str = "ibkr",
) -> dict[str, Any]:
```

And in the return dict (after `"generated_at"` line), add:
```python
        "data_source": data_source,
```

- [ ] **Step 3.6: Pass `data_source` from `run_portfolio_review()`**

In `tracker.py` at line 613, the `build_dashboard_json(...)` call currently doesn't pass `data_source`. Change it to:

```python
    dashboard = build_dashboard_json(
        position_table,
        unified_sector_allocation,
        hishtalmut_status,
        weekly_review["review_date"],
        cash=portfolio_input.cash,
        data_source=portfolio_input.kind,
    )
```

- [ ] **Step 3.7: Run full test suite**

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest tests/ -v
```

Expected: all tests pass (including existing `test_tracker.py` and `test_flex.py`).

- [ ] **Step 3.8: Commit**

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital
git add step5-portfolio-tracking/axe_portfolio/tracker.py step5-portfolio-tracking/tests/test_flex_fallback.py
git commit -m "feat: add Flex Query fallback in tracker.py and data_source field in portfolio.json"
```

---

## Task 4: Update `PortfolioPanel.jsx` — Dynamic Source Label

**Files:**
- Modify: `step6-dashboard/src/components/PortfolioPanel.jsx` (line 193)

- [ ] **Step 4.1: Replace hardcoded label**

In `step6-dashboard/src/components/PortfolioPanel.jsx`, find line 193:

```jsx
            IBKR snapshot · as of {data?.review_date || '—'}
```

Replace with:

```jsx
            {({ ibkr: 'IBKR live', flex: 'Flex Query (T+1)' })[data?.data_source] || 'IBKR'} · as of {data?.review_date || '—'}
```

- [ ] **Step 4.2: Verify the dev server renders correctly**

Start the dev environment and open the dashboard in a browser:

```bash
bash /home/tiger/.openclaw/workspace/projects/Axe-Capital/scripts/axe-dev.sh
```

Navigate to `http://localhost:5173`. In the Portfolio State panel, the subtitle line should read either:
- `IBKR live · as of 2026-04-20` (when live TWS data)
- `Flex Query (T+1) · as of 2026-04-20` (when Flex fallback was used)

Check browser console for React errors — there should be none.

- [ ] **Step 4.3: Commit**

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital
git add step6-dashboard/src/components/PortfolioPanel.jsx
git commit -m "feat: show data source label in PortfolioPanel (IBKR live vs Flex Query T+1)"
```

---

## Self-Review

**Spec coverage:**
- `flex.py` connector with two-step HTTP fetch → Tasks 1–2 ✓
- `FlexQueryConfig.from_env()` reading `AXE_IBKR_FLEX_TOKEN` / `AXE_IBKR_FLEX_QUERY_ID` → Task 1 ✓
- Skip `CASH`/`BAG`/`FXCFD` asset categories → Task 1 ✓
- Cash from `<CashReportCurrency currency="BASE">` → Task 1 ✓
- Derived fields: `market_value`, `unrealized_pl_pct` → Task 1 ✓
- `None` for `change_pct`, `pe`, `eps_current` → Task 1 ✓
- Poll with `_RETRY_SLEEP=3.0`, `_MAX_RETRIES=10` → Task 1 ✓
- All 5 error cases from spec → Task 2 ✓
- Fallback order: IBKR → Flex → raise → Task 3 ✓
- `data_source` in `portfolio.json` → Task 3 ✓
- `PortfolioInput.kind = "flex"` propagates to dashboard JSON → Task 3 ✓
- Dashboard source label → Task 4 ✓

**Placeholder scan:** No TBDs. All code blocks are complete.

**Type consistency:** `fetch_flex_portfolio()` returns `tuple[list[dict], float]` matching `fetch_ibkr_portfolio()`. `PortfolioInput.kind` is a plain `str` — no type change needed. `data_source` default `"ibkr"` preserves backward compatibility with existing CSV/raw/normalized paths.
