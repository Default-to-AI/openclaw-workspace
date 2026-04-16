# Portfolio Specialist Agents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the IBKR-portfolio specialist baseline: Fundamental, Technical, and Macro reports for every current portfolio symbol, then feed those reports into Step 3 decisions.

**Architecture:** Keep each specialist as its own step package. Add a small shared report-index helper in Step 8 and reuse the same index contract from Step 9/10. Step 7 orchestrates portfolio-wide runs by refreshing portfolio data, reading `portfolio.json`, and shelling out to each specialist package.

**Tech Stack:** Python 3.11+, pytest, yfinance, OpenAI chat completions, existing `axe_core` trace/path utilities, existing Step 7 FastAPI/CLI.

---

### Task 1: Report Index And Step 8 Test Coverage

**Files:**
- Create: `step8-fundamental/tests/test_reports.py`
- Create: `step8-fundamental/axe_fundamental/reports.py`
- Modify: `step8-fundamental/axe_fundamental/agent.py`

- [ ] **Step 1: Write failing tests**

```python
from __future__ import annotations

import json

from axe_fundamental.reports import update_report_index


def test_update_report_index_records_latest_agent_path(tmp_path):
    reports_dir = tmp_path / "analyst-reports"
    reports_dir.mkdir()
    report_path = reports_dir / "GOOG-fundamental-2026-04-16T00-00-00Z.json"
    report_path.write_text("{}", encoding="utf-8")

    index = update_report_index(reports_dir, "GOOG", "fundamental", report_path)

    assert index["symbols"]["GOOG"]["fundamental"]["json_path"] == "GOOG-fundamental-2026-04-16T00-00-00Z.json"
    assert json.loads((reports_dir / "index.json").read_text(encoding="utf-8")) == index
```

- [ ] **Step 2: Run red test**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step8-fundamental
pytest tests/test_reports.py -q
```

Expected: FAIL because `axe_fundamental.reports` does not exist.

- [ ] **Step 3: Implement report index helper**

```python
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def update_report_index(reports_dir: Path, ticker: str, agent: str, json_path: Path, md_path: Path | None = None) -> dict:
    reports_dir.mkdir(parents=True, exist_ok=True)
    index_path = reports_dir / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = {"generated_at": None, "symbols": {}}

    symbol = ticker.upper()
    index.setdefault("symbols", {}).setdefault(symbol, {})[agent] = {
        "json_path": json_path.name,
        "md_path": md_path.name if md_path else None,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    index["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp = index_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(index_path)
    return index
```

- [ ] **Step 4: Call helper from Step 8**

After Step 8 writes JSON and Markdown, call:

```python
update_report_index(reports_dir, ticker, "fundamental", json_path, md_path)
```

- [ ] **Step 5: Run green test**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step8-fundamental
pytest tests/test_reports.py -q
```

Expected: PASS.

---

### Task 2: Technical Analyst Package

**Files:**
- Create: `step9-technical/pyproject.toml`
- Create: `step9-technical/axe_technical/__init__.py`
- Create: `step9-technical/axe_technical/agent.py`
- Create: `step9-technical/axe_technical/cli.py`
- Create: `step9-technical/tests/test_agent.py`

- [ ] **Step 1: Write failing tests**

```python
from __future__ import annotations

from axe_technical.agent import build_technical_context, classify_trend


def test_classify_trend_uses_moving_average_relationship():
    assert classify_trend(last_price=110, sma_50=100, sma_200=90) == "uptrend"
    assert classify_trend(last_price=80, sma_50=90, sma_200=100) == "downtrend"
    assert classify_trend(last_price=95, sma_50=100, sma_200=90) == "mixed"


def test_build_technical_context_calculates_levels_from_history():
    rows = [
        {"Close": 10.0, "High": 11.0, "Low": 9.0, "Volume": 100},
        {"Close": 12.0, "High": 13.0, "Low": 10.0, "Volume": 150},
        {"Close": 11.0, "High": 12.0, "Low": 8.0, "Volume": 120},
    ]

    context = build_technical_context("goog", rows)

    assert context["ticker"] == "GOOG"
    assert context["last_price"] == 11.0
    assert context["support"] == 8.0
    assert context["resistance"] == 13.0
```

- [ ] **Step 2: Run red test**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step9-technical
pytest tests/test_agent.py -q
```

Expected: FAIL because package does not exist.

- [ ] **Step 3: Implement technical package**

Implement `classify_trend`, `build_technical_context`, `run_technical_analysis`, and a CLI entry point `axe-technical TICKER --force`. The runner writes JSON/Markdown reports and updates `analyst-reports/index.json`.

- [ ] **Step 4: Run green test**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step9-technical
pytest tests/test_agent.py -q
```

Expected: PASS.

---

### Task 3: Macro Analyst Package

**Files:**
- Create: `step10-macro/pyproject.toml`
- Create: `step10-macro/axe_macro/__init__.py`
- Create: `step10-macro/axe_macro/agent.py`
- Create: `step10-macro/axe_macro/cli.py`
- Create: `step10-macro/tests/test_agent.py`

- [ ] **Step 1: Write failing tests**

```python
from __future__ import annotations

from axe_macro.agent import infer_asset_context, normalize_macro_context


def test_infer_asset_context_identifies_etfs():
    context = infer_asset_context({"quoteType": "ETF", "category": "Large Growth"})

    assert context["instrument_type"] == "ETF"
    assert "Large Growth" in context["macro_exposures"]


def test_normalize_macro_context_has_uppercase_ticker_and_sector():
    context = normalize_macro_context("goog", {"sector": "Communication Services", "quoteType": "EQUITY"})

    assert context["ticker"] == "GOOG"
    assert context["sector"] == "Communication Services"
```

- [ ] **Step 2: Run red test**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step10-macro
pytest tests/test_agent.py -q
```

Expected: FAIL because package does not exist.

- [ ] **Step 3: Implement macro package**

Implement `infer_asset_context`, `normalize_macro_context`, `run_macro_analysis`, and a CLI entry point `axe-macro TICKER --force`. The runner writes JSON/Markdown reports and updates `analyst-reports/index.json`.

- [ ] **Step 4: Run green test**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step10-macro
pytest tests/test_agent.py -q
```

Expected: PASS.

---

### Task 4: Step 7 Specialist Orchestration

**Files:**
- Modify: `step7-automation/axe_orchestrator/runners.py`
- Modify: `step7-automation/axe_orchestrator/cli.py`
- Modify: `step7-automation/axe_orchestrator/api.py`
- Modify: `step7-automation/tests/test_cli.py`
- Modify: `step7-automation/tests/test_api.py`

- [ ] **Step 1: Write failing tests**

Add tests that prove:

```python
def test_portfolio_symbols_come_from_positive_positions(tmp_path):
    ...

def test_run_decision_accepts_ticker_argument(monkeypatch):
    ...

def test_cli_passes_ticker_to_runner(monkeypatch):
    ...
```

- [ ] **Step 2: Run red tests**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
pytest tests/test_cli.py tests/test_api.py -q
```

Expected: FAIL because specialist runners and ticker arguments are missing.

- [ ] **Step 3: Implement orchestration**

Add `portfolio_symbols`, `run_fundamental`, `run_technical`, `run_macro`, `run_specialists`, and `run_decision(ticker="MSFT")`. Add CLI support for `axe run decision GOOG` and `axe run specialists`.

- [ ] **Step 4: Run green tests**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
pytest tests/test_cli.py tests/test_api.py -q
```

Expected: PASS.

---

### Task 5: Step 3 Analyst Report Loading

**Files:**
- Modify: `step3-debate-decision/axe_decision/cli.py`
- Create: `step3-debate-decision/tests/test_analyst_reports.py`

- [ ] **Step 1: Write failing tests**

```python
from __future__ import annotations

import json

from axe_decision.cli import _load_analyst_reports


def test_load_analyst_reports_reads_latest_index(tmp_path, monkeypatch):
    reports = tmp_path / "analyst-reports"
    reports.mkdir()
    (reports / "GOOG-technical.json").write_text(json.dumps({"agent": "technical"}), encoding="utf-8")
    (reports / "index.json").write_text(json.dumps({
        "symbols": {"GOOG": {"technical": {"json_path": "GOOG-technical.json"}}}
    }), encoding="utf-8")
    monkeypatch.setattr("axe_decision.cli.public_dir", lambda: tmp_path)

    loaded = _load_analyst_reports("goog")

    assert loaded["technical"]["agent"] == "technical"
```

- [ ] **Step 2: Run red test**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step3-debate-decision
pytest tests/test_analyst_reports.py -q
```

Expected: FAIL because `_load_analyst_reports` does not exist.

- [ ] **Step 3: Implement report loading**

Add `_load_analyst_reports(ticker)` and include the result in `_load_context(ticker)` under `analyst_reports`.

- [ ] **Step 4: Run green test**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step3-debate-decision
pytest tests/test_analyst_reports.py -q
```

Expected: PASS.

---

### Task 6: Verification And Runbook Update

**Files:**
- Modify: `runbooks/prototype-launch.md`
- Modify: `_INDEX.md`

- [ ] **Step 1: Document user dashboard access**

Add the current user path:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital
./step7-automation/start_prototype.sh
xdg-open http://localhost:5173
```

- [ ] **Step 2: Document specialist baseline command**

Add:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation
python -m axe_orchestrator.cli run specialists
```

- [ ] **Step 3: Run verification**

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step8-fundamental && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step9-technical && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step10-macro && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step3-debate-decision && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step6-dashboard && npm run build
```

Expected: all commands exit 0.

