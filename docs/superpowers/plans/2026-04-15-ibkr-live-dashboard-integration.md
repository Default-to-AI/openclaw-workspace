# IBKR Live Dashboard Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the Axe Capital dashboard’s `step6-dashboard/public/portfolio.json` from a live Interactive Brokers (IBKR) account using a read-only `ib_async` connection (no order execution).

**Architecture:** A Step 5 Python adapter connects locally to TWS/IB Gateway via `ib_async`, reads portfolio/account data, normalizes it to the dashboard contract, and writes JSON/CSV artifacts. Step 7 exposes a `POST /refresh/portfolio` endpoint that runs the Step 5 CLI. Step 6 (React/Vite) triggers refresh via `/api/refresh/{target}` and falls back to static artifacts for read-only rendering.

**Tech Stack:** Python 3.11+, `ib_async`, `pytest`, FastAPI (Step 7), React/Vite (Step 6), artifact files under `step6-dashboard/public/`.

---

## Spec Source

This plan implements the runbook:
- `.openclaw/workspace/projects/Axe-Capital/runbooks/ibkr-live-dashboard-integration.md`

## Non-Goals (Hard Safety Boundaries)

- No order placement from dashboard refresh path.
- No IBKR credentials in frontend code.
- No storing IB passwords in repo files.
- Read-only connections only (`readonly=True`).

## File Map (Decomposition Locked In)

**Step 5 (portfolio tracking)**
- Create: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/ibkr.py` (read-only IBKR adapter + normalization)
- Modify: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/tracker.py` (source selection: `csv|ibkr|auto`, artifact writing)
- Modify: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/cli.py` (trace-wrapped entrypoint)
- Modify: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/pyproject.toml` (dependency: `ib_async`, packaging)
- Create: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_ibkr.py` (unit tests with fake `IB`)
- Create: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_tracker_source.py` (unit tests for source selection)

**Step 7 (automation + API)**
- Modify: `.openclaw/workspace/projects/Axe-Capital/step7-automation/axe_orchestrator/runners.py` (runner for `portfolio`)
- Modify: `.openclaw/workspace/projects/Axe-Capital/step7-automation/axe_orchestrator/api.py` (enable `portfolio` in refresh map)

**Step 6 (dashboard)**
- Modify: `.openclaw/workspace/projects/Axe-Capital/step6-dashboard/src/lib/api.js` (POST refresh helper)
- Modify: `.openclaw/workspace/projects/Axe-Capital/step6-dashboard/src/components/RefreshBar.jsx` (button wiring for `portfolio`)

**Docs**
- Modify: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/README.md` (IBKR env + usage)
- Modify: `.openclaw/workspace/projects/Axe-Capital/step7-automation/README.md` (refresh endpoint usage)

---

### Task 0: Worktree + Local Dev Setup

**Files:**
- Modify: none

- [ ] **Step 1: Create a dedicated worktree**

Run (from repo root):
```bash
git worktree add -b feat/ibkr-live-dashboard .worktrees/ibkr-live-dashboard main
cd .worktrees/ibkr-live-dashboard
```

- [ ] **Step 2: Install Step 0 + Step 5 editable deps**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step0-shared
uv pip install -e .

cd ../step5-portfolio-tracking
uv pip install -e .
python -c "import axe_core; import axe_portfolio; print('ok')"
```

Expected: prints `ok`.

- [ ] **Step 3: Confirm tests run**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest -q
```

Expected: PASS (or at least confirms the test harness executes).

- [ ] **Step 4: Commit (setup only if needed)**

If you changed anything during setup (ideally you didn’t):
```bash
git status --porcelain
```

---

### Task 1: IBKR Read-Only Adapter (Normalization + Cash Extraction)

**Files:**
- Create: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_ibkr.py`
- Create: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/ibkr.py`
- Modify: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/pyproject.toml`

- [ ] **Step 1: Write the failing test for live snapshot mapping**

Create `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_ibkr.py`:
```python
from __future__ import annotations

from dataclasses import dataclass

from axe_portfolio.ibkr import IBKRConnectionConfig, fetch_ibkr_portfolio


@dataclass
class _Contract:
    symbol: str
    secType: str = "STK"
    localSymbol: str = ""


@dataclass
class _PortfolioItem:
    contract: _Contract
    position: float
    marketPrice: float
    averageCost: float
    marketValue: float
    unrealizedPNL: float


@dataclass
class _AccountValue:
    tag: str
    value: str
    currency: str = "USD"


class _FakeIB:
    connected_with = None
    disconnected = False

    def connect(self, *args, **kwargs):
        type(self).connected_with = (args, kwargs)

    def managedAccounts(self):
        return ["DU123"]

    def portfolio(self, account=None):
        assert account == "DU123"
        return [
            _PortfolioItem(_Contract("MSFT"), 2, 425.5, 400.0, 851.0, 51.0),
            _PortfolioItem(_Contract("USD", "CASH"), 1000, 1, 1, 1000, 0),
        ]

    def accountSummary(self, account=None):
        assert account == "DU123"
        return [_AccountValue("TotalCashValue", "1234.56")]

    def disconnect(self):
        type(self).disconnected = True


def test_fetch_ibkr_portfolio_maps_live_snapshot():
    config = IBKRConnectionConfig(host="localhost", port=4001, client_id=77, timeout=3)

    rows, cash = fetch_ibkr_portfolio(config=config, ib_factory=_FakeIB)

    assert cash == 1234.56
    assert rows == [
        {
            "symbol": "MSFT",
            "position": 2.0,
            "last": 425.5,
            "change_pct": None,
            "avg_price": 400.0,
            "cost_basis": 800.0,
            "market_value": 851.0,
            "unrealized_pl": 51.0,
            "unrealized_pl_pct": 6.38,
            "pe": None,
            "eps_current": None,
        }
    ]
    assert _FakeIB.connected_with == (
        ("localhost", 4001),
        {"clientId": 77, "timeout": 3, "readonly": True, "account": ""},
    )
    assert _FakeIB.disconnected is True
```

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest -q tests/test_ibkr.py::test_fetch_ibkr_portfolio_maps_live_snapshot
```

Expected: FAIL (module/function not implemented yet).

- [ ] **Step 3: Add `ib_async` dependency**

Modify `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/pyproject.toml`:
```toml
[project]
dependencies = [
  "axe-core",
  "ib_async>=2.1",
  "pandas>=2.2",
  "python-dotenv>=1.0",
  "yfinance>=0.2.50",
]
```

- [ ] **Step 4: Implement the minimal adapter**

Create `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/ibkr.py`:
```python
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from axe_portfolio.util import safe_float as _safe_float


@dataclass(frozen=True)
class IBKRConnectionConfig:
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 51
    account: str | None = None
    timeout: float = 10.0
    readonly: bool = True

    @classmethod
    def from_env(cls) -> "IBKRConnectionConfig":
        return cls(
            host=os.getenv("AXE_IBKR_HOST", "127.0.0.1"),
            port=int(os.getenv("AXE_IBKR_PORT", "7497")),
            client_id=int(os.getenv("AXE_IBKR_CLIENT_ID", "51")),
            account=os.getenv("AXE_IBKR_ACCOUNT") or None,
            timeout=float(os.getenv("AXE_IBKR_TIMEOUT", "10")),
            readonly=os.getenv("AXE_IBKR_READONLY", "1").lower() not in {"0", "false", "no"},
        )


def _require_ib_class() -> type:
    try:
        from ib_async import IB
    except ImportError as exc:
        raise RuntimeError(
            "ib_async is not installed. Install step5 dependencies, then run with "
            "AXE_PORTFOLIO_SOURCE=ibkr."
        ) from exc
    return IB


def _symbol_from_contract(contract: Any) -> str:
    local_symbol = str(getattr(contract, "localSymbol", "") or "").strip()
    symbol = str(getattr(contract, "symbol", "") or "").strip()
    return symbol or local_symbol


def _row_from_portfolio_item(item: Any) -> dict[str, Any] | None:
    contract = getattr(item, "contract", None)
    symbol = _symbol_from_contract(contract)
    if not symbol:
        return None
    sec_type = str(getattr(contract, "secType", "") or "").upper()
    if sec_type in {"CASH", "BAG"}:
        return None

    position = _safe_float(getattr(item, "position", None)) or 0.0
    last = _safe_float(getattr(item, "marketPrice", None)) or 0.0
    avg_price = _safe_float(getattr(item, "averageCost", None)) or 0.0
    market_value = _safe_float(getattr(item, "marketValue", None))
    if market_value is None:
        market_value = round(position * last, 2)
    cost_basis = round(position * avg_price, 2)
    unrealized_pl = _safe_float(getattr(item, "unrealizedPNL", None))
    if unrealized_pl is None:
        unrealized_pl = round(market_value - cost_basis, 2)
    unrealized_pl_pct = round((unrealized_pl / cost_basis) * 100, 2) if cost_basis else None

    return {
        "symbol": symbol,
        "position": position,
        "last": last,
        "change_pct": None,
        "avg_price": avg_price,
        "cost_basis": cost_basis,
        "market_value": round(market_value, 2),
        "unrealized_pl": round(unrealized_pl, 2),
        "unrealized_pl_pct": unrealized_pl_pct,
        "pe": None,
        "eps_current": None,
    }


def _row_from_position(position_item: Any) -> dict[str, Any] | None:
    contract = getattr(position_item, "contract", None)
    symbol = _symbol_from_contract(contract)
    if not symbol:
        return None
    sec_type = str(getattr(contract, "secType", "") or "").upper()
    if sec_type in {"CASH", "BAG"}:
        return None

    position = _safe_float(getattr(position_item, "position", None)) or 0.0
    avg_price = _safe_float(getattr(position_item, "avgCost", None)) or 0.0
    return {
        "symbol": symbol,
        "position": position,
        "last": avg_price,
        "change_pct": None,
        "avg_price": avg_price,
        "cost_basis": round(position * avg_price, 2),
        "market_value": round(position * avg_price, 2),
        "unrealized_pl": 0.0,
        "unrealized_pl_pct": 0.0,
        "pe": None,
        "eps_current": None,
    }


def _managed_account(ib: Any, requested_account: str | None) -> str | None:
    if requested_account:
        return requested_account
    try:
        accounts = list(ib.managedAccounts())
    except Exception:
        return None
    return accounts[0] if accounts else None


def _portfolio_items(ib: Any, account: str | None) -> list[Any]:
    try:
        return list(ib.portfolio(account)) if account else list(ib.portfolio())
    except TypeError:
        return list(ib.portfolio())


def _position_items(ib: Any, account: str | None) -> list[Any]:
    try:
        items = list(ib.positions(account)) if account else list(ib.positions())
    except TypeError:
        items = list(ib.positions())
    if account:
        items = [item for item in items if getattr(item, "account", account) == account]
    return items


def _cash_from_account_summary(ib: Any, account: str | None) -> float:
    try:
        summary = ib.accountSummary(account) if account else ib.accountSummary()
    except TypeError:
        summary = ib.accountSummary()
    except Exception:
        return 0.0

    preferred_tags = {"TotalCashValue", "CashBalance"}
    fallback = 0.0
    for item in summary:
        tag = str(getattr(item, "tag", "") or "")
        currency = str(getattr(item, "currency", "") or "").upper()
        value = _safe_float(getattr(item, "value", None))
        if value is None:
            continue
        if tag == "NetLiquidation" and currency in {"", "BASE", "USD"}:
            fallback = value
        if tag in preferred_tags and currency in {"", "BASE", "USD"}:
            return value
    return fallback


def fetch_ibkr_portfolio(
    config: IBKRConnectionConfig | None = None,
    ib_factory: type | None = None,
) -> tuple[list[dict[str, Any]], float]:
    cfg = config or IBKRConnectionConfig.from_env()
    IB = ib_factory or _require_ib_class()
    ib = IB()
    try:
        ib.connect(
            cfg.host,
            cfg.port,
            clientId=cfg.client_id,
            timeout=cfg.timeout,
            readonly=cfg.readonly,
            account=cfg.account or "",
        )
        account = _managed_account(ib, cfg.account)
        rows = [
            row
            for row in (_row_from_portfolio_item(item) for item in _portfolio_items(ib, account))
            if row is not None
        ]
        if not rows:
            rows = [
                row
                for row in (_row_from_position(item) for item in _position_items(ib, account))
                if row is not None
            ]
        cash = _cash_from_account_summary(ib, account)
        return rows, cash
    finally:
        try:
            ib.disconnect()
        except Exception:
            pass
```

- [ ] **Step 5: Run tests to verify they pass**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest -q tests/test_ibkr.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:
```bash
git add \
  .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/pyproject.toml \
  .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/ibkr.py \
  .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_ibkr.py
git commit -m "feat(portfolio): add read-only IBKR adapter via ib_async"
```

---

### Task 2: Portfolio Source Selection (`csv|ibkr|auto`) + Artifact Writing

**Files:**
- Modify: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/tracker.py`
- Create: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_tracker_source.py`

- [ ] **Step 1: Write the failing test for source selection**

Create `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_tracker_source.py`:
```python
from __future__ import annotations

import os

from axe_portfolio import tracker as tracker_mod


def test_resolve_portfolio_input_uses_ibkr_when_enabled(monkeypatch):
    monkeypatch.setenv("AXE_PORTFOLIO_SOURCE", "ibkr")

    def fake_fetch():
        return (
            [
                {
                    "symbol": "MSFT",
                    "position": 1.0,
                    "last": 100.0,
                    "change_pct": None,
                    "avg_price": 90.0,
                    "cost_basis": 90.0,
                    "market_value": 100.0,
                    "unrealized_pl": 10.0,
                    "unrealized_pl_pct": 11.11,
                    "pe": None,
                    "eps_current": None,
                }
            ],
            50.0,
        )

    monkeypatch.setattr(tracker_mod, "fetch_ibkr_portfolio", lambda: fake_fetch())

    inp = tracker_mod._resolve_portfolio_input()

    assert inp.kind == "ibkr"
    assert inp.cash == 50.0
    assert inp.rows[0]["symbol"] == "MSFT"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest -q tests/test_tracker_source.py::test_resolve_portfolio_input_uses_ibkr_when_enabled
```

Expected: FAIL until `_resolve_portfolio_input()` supports `AXE_PORTFOLIO_SOURCE=ibkr`.

- [ ] **Step 3: Implement source selection in tracker**

Modify `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/tracker.py` so `_resolve_portfolio_input()` starts with:
```python
def _resolve_portfolio_input() -> PortfolioInput:
    source = os.getenv("AXE_PORTFOLIO_SOURCE", "csv").strip().lower()
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
```

…and then falls back to the existing CSV discovery logic when in `auto` mode or `csv` mode.

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest -q tests/test_tracker_source.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:
```bash
git add \
  .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/tracker.py \
  .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_tracker_source.py
git commit -m "feat(portfolio): add ibkr/auto source selection for tracker"
```

---

### Task 3: Trace-Wrapped CLI Entry Point (Step 5)

**Files:**
- Modify: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/cli.py`
- Test: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_cli_trace.py`

- [ ] **Step 1: Write failing tests for trace success/failure**

Create `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_cli_trace.py`:
```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from axe_portfolio import cli as portfolio_cli
from axe_core import trace as trace_mod


@dataclass
class _FakeArtifacts:
    normalized_csv_path: Path
    weekly_review_path: Path
    position_table: list
    unified_sector_allocation: dict
    spy_comparison: dict
    hishtalmut_status: dict


def test_cli_emits_trace_success(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)

    fake = _FakeArtifacts(
        normalized_csv_path=tmp_path / "norm.csv",
        weekly_review_path=tmp_path / "weekly.json",
        position_table=[{"ticker": "MSFT"}, {"ticker": "GOOG"}],
        unified_sector_allocation={"Tech": 0.5},
        spy_comparison={"ytd": 0.03},
        hishtalmut_status={"ok": True},
    )
    monkeypatch.setattr(portfolio_cli, "run_portfolio_review", lambda: fake)

    portfolio_cli.main()

    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert index["runs"][0]["agent"] == "axe_portfolio"
    assert index["runs"][0]["status"] == "success"
    assert index["runs"][0]["artifact_written"] == "portfolio.json"


def test_cli_records_failure(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)

    def boom():
        raise FileNotFoundError("IBKR CSV missing")

    monkeypatch.setattr(portfolio_cli, "run_portfolio_review", boom)

    try:
        portfolio_cli.main()
    except FileNotFoundError:
        pass

    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert index["runs"][0]["agent"] == "axe_portfolio"
    assert index["runs"][0]["status"] == "failed"
```

- [ ] **Step 2: Run tests to verify failure**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest -q tests/test_cli_trace.py
```

Expected: FAIL until CLI writes trace index entries.

- [ ] **Step 3: Implement trace-wrapped CLI**

Modify `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/cli.py` to:
```python
from __future__ import annotations

import json

from axe_core import Tracer
from axe_portfolio.tracker import run_portfolio_review


def main() -> None:
    tracer = Tracer(agent="axe_portfolio")
    tracer.start()
    tracer.event(step="load_inputs", thought="reading IBKR CSV + portfolio snapshot")

    try:
        artifacts = run_portfolio_review()
    except Exception as exc:
        tracer.event(step="error", thought=f"review failed: {exc}")
        tracer.finalize(status="failed", summary=f"review failed: {exc}", artifact_written=None)
        raise

    n_positions = len(artifacts.position_table)
    tracer.event(
        step="review_complete",
        thought=f"normalized {n_positions} positions",
        io={"out": {"positions": n_positions}},
    )
    tracer.finalize(
        status="success",
        summary=f"portfolio review — {n_positions} positions",
        artifact_written="portfolio.json",
    )

    print(
        json.dumps(
            {
                "normalized_csv_path": str(artifacts.normalized_csv_path),
                "weekly_review_path": str(artifacts.weekly_review_path),
                "position_table": artifacts.position_table,
                "unified_sector_allocation": artifacts.unified_sector_allocation,
                "spy_comparison": artifacts.spy_comparison,
                "hishtalmut_status": artifacts.hishtalmut_status,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
pytest -q tests/test_cli_trace.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:
```bash
git add \
  .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/axe_portfolio/cli.py \
  .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/tests/test_cli_trace.py
git commit -m "feat(portfolio): add trace-wrapped portfolio CLI entrypoint"
```

---

### Task 4: Step 7 Orchestrator Runner + Refresh Endpoint Support

**Files:**
- Modify: `.openclaw/workspace/projects/Axe-Capital/step7-automation/axe_orchestrator/runners.py`
- Modify: `.openclaw/workspace/projects/Axe-Capital/step7-automation/axe_orchestrator/api.py`

- [ ] **Step 1: Add `run_portfolio()` runner**

Modify `.openclaw/workspace/projects/Axe-Capital/step7-automation/axe_orchestrator/runners.py`:
```python
def run_portfolio() -> int:
    return _run_module("axe_portfolio.cli", "step5-portfolio-tracking")
```

- [ ] **Step 2: Wire `portfolio` into refresh map**

Modify `.openclaw/workspace/projects/Axe-Capital/step7-automation/axe_orchestrator/api.py`:
```python
AGENT_RUNNERS: dict[str, Callable[[], int]] = {
    "portfolio": runners.run_portfolio,
    "alpha": runners.run_alpha,
    "news": runners.run_news,
    "decision": runners.run_decision,
}
```

- [ ] **Step 3: Run Step 7 tests**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step7-automation
pytest -q
```

Expected: PASS.

- [ ] **Step 4: Commit**

Run:
```bash
git add \
  .openclaw/workspace/projects/Axe-Capital/step7-automation/axe_orchestrator/runners.py \
  .openclaw/workspace/projects/Axe-Capital/step7-automation/axe_orchestrator/api.py
git commit -m "feat(api): enable portfolio refresh via orchestrator"
```

---

### Task 5: Step 6 Dashboard Refresh Button (Portfolio)

**Files:**
- Modify: `.openclaw/workspace/projects/Axe-Capital/step6-dashboard/src/lib/api.js`
- Modify: `.openclaw/workspace/projects/Axe-Capital/step6-dashboard/src/components/RefreshBar.jsx`

- [ ] **Step 1: Ensure API helper posts to `/api/refresh/{target}`**

Modify `.openclaw/workspace/projects/Axe-Capital/step6-dashboard/src/lib/api.js` to include:
```js
export async function triggerRefresh(target) {
  const response = await fetch(`/api/refresh/${encodeURIComponent(target)}`, {
    method: 'POST',
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const payload = await response.json()
      detail = payload.detail || detail
    } catch {
      // ignore, keep generic detail
    }
    throw new Error(detail)
  }

  return response.json()
}
```

- [ ] **Step 2: Add `portfolio` target button**

Modify `.openclaw/workspace/projects/Axe-Capital/step6-dashboard/src/components/RefreshBar.jsx`:
```js
const TARGETS = [
  { id: 'all', label: 'Run all' },
  { id: 'portfolio', label: 'Portfolio' },
  { id: 'alpha', label: 'Alpha' },
  { id: 'news', label: 'News' },
  { id: 'decision', label: 'Decision' },
]
```

- [ ] **Step 3: Run the dashboard in dev mode (manual)**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step6-dashboard
npm install
npm run dev
```

Expected: UI shows `Portfolio` refresh button under “System State”.

- [ ] **Step 4: Commit**

Run:
```bash
git add \
  .openclaw/workspace/projects/Axe-Capital/step6-dashboard/src/lib/api.js \
  .openclaw/workspace/projects/Axe-Capital/step6-dashboard/src/components/RefreshBar.jsx
git commit -m "feat(dashboard): add portfolio refresh control"
```

---

### Task 6: End-to-End Smoke Test (Real TWS/IB Gateway) + Docs

**Files:**
- Modify: `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/README.md`
- Modify: `.openclaw/workspace/projects/Axe-Capital/step7-automation/README.md`

- [ ] **Step 1: Configure TWS/IB Gateway locally**

In TWS/IB Gateway:
```text
Configure -> API -> Settings
  [x] Enable ActiveX and Socket Clients
  Trusted IPs: 127.0.0.1
  Port: 7497 (TWS) or 4001 (Gateway)
  [x] Download open orders on connection
```

- [ ] **Step 2: Run Step 5 in strict IBKR mode**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking
AXE_PORTFOLIO_SOURCE=ibkr \
AXE_IBKR_HOST=127.0.0.1 \
AXE_IBKR_PORT=7497 \
AXE_IBKR_CLIENT_ID=51 \
AXE_IBKR_READONLY=1 \
python -m axe_portfolio.cli
```

Expected:
- exits `0`
- prints JSON with `position_table`
- refreshes `.openclaw/workspace/projects/Axe-Capital/step6-dashboard/public/portfolio.json`

- [ ] **Step 3: Run Step 7 API and trigger refresh**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital/step7-automation
uvicorn axe_orchestrator.api:app --reload --port 8000
```

In a second terminal:
```bash
curl -s -X POST http://localhost:8000/refresh/portfolio | jq
```

Expected: JSON with `"target": "portfolio"` and `"ok": true`.

- [ ] **Step 4: Safety scan (ensure no order placement)**

Run:
```bash
cd .openclaw/workspace/projects/Axe-Capital
rg -n "placeOrder\\(" step5-portfolio-tracking/axe_portfolio
```

Expected: no matches.

- [ ] **Step 5: Document env vars + usage**

Update `.openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/README.md` with:
```text
AXE_PORTFOLIO_SOURCE=csv|ibkr|auto
AXE_IBKR_HOST=127.0.0.1
AXE_IBKR_PORT=7497
AXE_IBKR_CLIENT_ID=51
AXE_IBKR_ACCOUNT=DU1234567 (optional)
AXE_IBKR_READONLY=1
AXE_IBKR_TIMEOUT=10
```

And add:
```bash
AXE_PORTFOLIO_SOURCE=ibkr python -m axe_portfolio.cli
```

Update `.openclaw/workspace/projects/Axe-Capital/step7-automation/README.md` with:
```bash
POST /refresh/portfolio
```

- [ ] **Step 6: Commit**

Run:
```bash
git add \
  .openclaw/workspace/projects/Axe-Capital/step5-portfolio-tracking/README.md \
  .openclaw/workspace/projects/Axe-Capital/step7-automation/README.md
git commit -m "docs: add IBKR live refresh configuration and usage"
```

---

## Self-Review Checklist (Do This Before Handing Off)

1. **Spec coverage:** Confirm the plan covers: read-only IBKR connection, portfolio rows, cash summary, artifact refresh to `step6-dashboard/public/portfolio.json`, Step 7 refresh endpoint, and dashboard refresh UI.
2. **Placeholder scan:** Search this plan for `TODO`, `TBD`, “appropriate”, “handle edge cases” and remove/replace with concrete steps.
3. **Type consistency:** Verify `IBKRConnectionConfig`, `fetch_ibkr_portfolio()`, and `_resolve_portfolio_input()` signatures match across tasks/tests.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-15-ibkr-live-dashboard-integration.md`. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks
2. **Inline Execution** — execute tasks in this session in batches with checkpoints

Which approach?

