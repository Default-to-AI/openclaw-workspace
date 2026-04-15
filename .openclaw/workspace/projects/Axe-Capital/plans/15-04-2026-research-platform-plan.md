# Axe Capital Research Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the Axe Capital dashboard from portfolio monitor into research-assist platform with 7 panels, agent traces, news ingestion, and thin FastAPI backend.

**Architecture:** New shared `axe_core` package provides `trace` library + path helpers + pydantic schemas; all agent packages depend on it and emit trace JSON into `step6-dashboard/public/`. New `axe_news` package ingests RSS + LLM-scores impact. `axe_orchestrator` is the single CLI (later FastAPI) entrypoint. React dashboard renders pure JSON artifacts with API-optional degradation.

**Tech Stack:** Python 3.11 (pytest, pydantic, httpx, feedparser, anthropic), Node 20 / React 19 / Vite 8 / Tailwind 3, FastAPI + uvicorn + sse-starlette (week 4 only).

**Spec:** `projects/Axe-Capital/spec/15-04-2026-research-platform-design.md`

**Plan location conventions:**
- Python packages live under `projects/Axe-Capital/stepN-*/`
- All artifacts written to `projects/Axe-Capital/step6-dashboard/public/`
- Tests live under each package's `tests/` dir
- All commands assume CWD = `projects/Axe-Capital/` unless noted

---

## Task 1: Scaffold `axe_core` package

**Files:**
- Create: `step0-shared/axe_core/__init__.py`
- Create: `step0-shared/axe_core/paths.py`
- Create: `step0-shared/pyproject.toml`
- Create: `step0-shared/tests/__init__.py`
- Create: `step0-shared/tests/test_paths.py`

- [ ] **Step 1: Create directory layout**

```bash
mkdir -p step0-shared/axe_core step0-shared/tests
```

- [ ] **Step 2: Write `pyproject.toml`**

Create `step0-shared/pyproject.toml`:

```toml
[project]
name = "axe-core"
version = "0.1.0"
description = "Axe Capital shared utilities: trace, paths, schemas"
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2.6",
]

[project.optional-dependencies]
test = ["pytest>=8.0"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["axe_core*"]
```

- [ ] **Step 3: Write failing test for `paths.py`**

Create `step0-shared/tests/test_paths.py`:

```python
from pathlib import Path

from axe_core.paths import project_root, public_dir, traces_dir


def test_project_root_is_axe_capital_dir():
    root = project_root()
    assert root.name == "Axe-Capital"
    assert (root / "CLAUDE.md").exists()


def test_public_dir_points_to_step6_public():
    assert public_dir() == project_root() / "step6-dashboard" / "public"


def test_traces_dir_is_public_slash_traces(tmp_path, monkeypatch):
    assert traces_dir() == public_dir() / "traces"
```

- [ ] **Step 4: Run test to confirm failure**

```bash
cd step0-shared && pip install -e .[test] && pytest tests/test_paths.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'axe_core.paths'`.

- [ ] **Step 5: Implement `paths.py`**

Create `step0-shared/axe_core/paths.py`:

```python
"""Canonical filesystem paths for the Axe Capital project."""
from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the Axe-Capital project root, found by walking up for CLAUDE.md."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if parent.name == "Axe-Capital" and (parent / "CLAUDE.md").exists():
            return parent
    raise RuntimeError("Could not locate Axe-Capital project root from axe_core")


def public_dir() -> Path:
    return project_root() / "step6-dashboard" / "public"


def traces_dir() -> Path:
    return public_dir() / "traces"
```

Create `step0-shared/axe_core/__init__.py`:

```python
"""axe_core — shared utilities for Axe Capital agents."""
from axe_core.paths import project_root, public_dir, traces_dir

__all__ = ["project_root", "public_dir", "traces_dir"]
```

- [ ] **Step 6: Run test to confirm pass**

```bash
cd step0-shared && pytest tests/test_paths.py -v
```

Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add step0-shared/
git commit -m "feat(axe_core): scaffold shared package with paths helper"
```

---

## Task 2: `axe_core.trace` — emit, finalize, prune

**Files:**
- Create: `step0-shared/axe_core/trace.py`
- Create: `step0-shared/tests/test_trace.py`

The trace library captures one agent run: a JSON file `traces/<run-id>.json` with per-step events, plus an atomic update to `traces/index.json` on finalize. Pruning keeps newest 50 runs per agent, cap 500 global, and deletes orphaned trace files.

- [ ] **Step 1: Write failing test for `Tracer` happy path**

Create `step0-shared/tests/test_trace.py`:

```python
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from axe_core import trace as trace_mod
from axe_core.trace import Tracer


@pytest.fixture
def fake_public(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)
    (tmp_path / "traces").mkdir()
    return tmp_path


def test_tracer_writes_trace_file_and_index_entry(fake_public):
    t = Tracer(agent="axe_alpha", now=lambda: datetime(2026, 4, 15, 9, 0, tzinfo=timezone.utc))
    t.start()
    t.event(step="scan", thought="looking", io={"in": {"n": 1}, "out": {"n": 2}})
    t.event(step="done", thought="finished")
    t.finalize(status="success", summary="ran 2 steps", artifact_written="alpha-latest.json")

    trace_path = fake_public / "traces" / f"{t.run_id}.json"
    assert trace_path.exists()
    data = json.loads(trace_path.read_text())
    assert data["agent"] == "axe_alpha"
    assert data["status"] == "success"
    assert data["summary"] == "ran 2 steps"
    assert len(data["events"]) == 2
    assert data["events"][0]["seq"] == 1
    assert data["events"][1]["seq"] == 2

    index = json.loads((fake_public / "traces" / "index.json").read_text())
    assert len(index["runs"]) == 1
    assert index["runs"][0]["run_id"] == t.run_id
    assert index["runs"][0]["event_count"] == 2
    assert index["runs"][0]["artifact_written"] == "alpha-latest.json"


def test_run_id_uses_dd_mm_yyyy_format(fake_public):
    t = Tracer(agent="axe_alpha", now=lambda: datetime(2026, 4, 15, 9, 0, 0, tzinfo=timezone.utc))
    t.start()
    assert t.run_id.startswith("alpha-15-04-2026T09-00-00Z")


def test_finalize_is_atomic_via_tmp_rename(fake_public, monkeypatch):
    calls = []
    real_replace = Path.replace

    def spy(self, target):
        calls.append((self.name, Path(target).name))
        return real_replace(self, target)

    monkeypatch.setattr(Path, "replace", spy)
    t = Tracer(agent="axe_alpha")
    t.start()
    t.finalize(status="success", summary="ok")
    assert ("index.json.tmp", "index.json") in calls


def test_prune_keeps_newest_50_per_agent(fake_public):
    # Seed 60 fake alpha runs with prepopulated trace files
    now = datetime(2026, 4, 15, 9, 0, tzinfo=timezone.utc)
    for i in range(60):
        tr = Tracer(
            agent="axe_alpha",
            now=lambda i=i: datetime(2026, 4, 15, 9, i, 0, tzinfo=timezone.utc),
        )
        tr.start()
        tr.finalize(status="success", summary=f"run {i}")

    index = json.loads((fake_public / "traces" / "index.json").read_text())
    assert len(index["runs"]) == 50
    trace_files = list((fake_public / "traces").glob("alpha-*.json"))
    assert len(trace_files) == 50


def test_failed_runs_recorded_with_status(fake_public):
    t = Tracer(agent="axe_news")
    t.start()
    t.event(step="fetch", thought="fetching")
    t.finalize(status="failed", summary="RSS 500", artifact_written=None)
    data = json.loads((fake_public / "traces" / f"{t.run_id}.json").read_text())
    assert data["status"] == "failed"
    index = json.loads((fake_public / "traces" / "index.json").read_text())
    assert index["runs"][0]["status"] == "failed"
```

- [ ] **Step 2: Run tests, confirm they fail**

```bash
cd step0-shared && pytest tests/test_trace.py -v
```

Expected: FAIL with `ImportError: cannot import name 'trace' from 'axe_core'`.

- [ ] **Step 3: Implement `trace.py`**

Create `step0-shared/axe_core/trace.py`:

```python
"""Agent trace library — one trace file per run, atomic index updates, pruning."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal

from axe_core.paths import traces_dir

AGENT_SHORT = {
    "axe_alpha": "alpha",
    "axe_news": "news",
    "axe_portfolio": "portfolio",
    "axe_coo": "coo",
    "axe_orchestrator": "orch",
}
MAX_PER_AGENT = 50
GLOBAL_CAP = 500
Status = Literal["success", "failed", "partial"]


def _public_dir() -> Path:
    # Indirection so tests can monkeypatch the base dir.
    return traces_dir().parent


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _fmt_run_id(agent: str, ts: datetime) -> str:
    short = AGENT_SHORT.get(agent, agent)
    stamp = ts.strftime("%d-%m-%YT%H-%M-%SZ")
    return f"{short}-{stamp}"


def _atomic_write_json(path: Path, data: Any) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=False))
    tmp.replace(path)


@dataclass
class Tracer:
    agent: str
    now: Callable[[], datetime] = field(default=_now_utc)
    run_id: str = ""
    started_at: str = ""
    _events: list[dict[str, Any]] = field(default_factory=list)
    _seq: int = 0
    _artifact_written: str | None = None

    def start(self) -> None:
        ts = self.now()
        self.run_id = _fmt_run_id(self.agent, ts)
        self.started_at = ts.strftime("%Y-%m-%dT%H:%M:%SZ")

    def event(
        self,
        step: str,
        thought: str = "",
        io: dict[str, Any] | None = None,
        rejected: list[str] | None = None,
        elapsed_ms: int | None = None,
    ) -> None:
        self._seq += 1
        entry: dict[str, Any] = {
            "seq": self._seq,
            "t": self.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
            "step": step,
            "thought": thought,
        }
        if io is not None:
            entry["io"] = io
        if rejected is not None:
            entry["rejected"] = rejected
        if elapsed_ms is not None:
            entry["elapsed_ms"] = elapsed_ms
        self._events.append(entry)

    def finalize(
        self,
        status: Status,
        summary: str,
        artifact_written: str | None = None,
    ) -> None:
        ended = self.now()
        ended_str = ended.strftime("%Y-%m-%dT%H:%M:%SZ")
        duration_ms = self._duration_ms(ended)

        trace_dir = _public_dir() / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        trace_path = trace_dir / f"{self.run_id}.json"
        _atomic_write_json(
            trace_path,
            {
                "run_id": self.run_id,
                "agent": self.agent,
                "started_at": self.started_at,
                "ended_at": ended_str,
                "status": status,
                "summary": summary,
                "events": self._events,
            },
        )

        index_path = trace_dir / "index.json"
        index = _load_index(index_path)
        new_entry = {
            "run_id": self.run_id,
            "agent": self.agent,
            "started_at": self.started_at,
            "ended_at": ended_str,
            "duration_ms": duration_ms,
            "status": status,
            "event_count": len(self._events),
            "summary": summary,
            "artifact_written": artifact_written,
        }
        index["runs"] = [new_entry] + [r for r in index["runs"] if r["run_id"] != self.run_id]
        index["generated_at"] = ended_str
        _prune(index, trace_dir)
        index["retention"] = {"max_runs_per_agent": MAX_PER_AGENT, "total_cap": GLOBAL_CAP}
        _atomic_write_json(index_path, index)

    def _duration_ms(self, ended: datetime) -> int:
        started = datetime.strptime(self.started_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return int((ended - started).total_seconds() * 1000)


def _load_index(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text())
    return {"generated_at": "", "retention": {}, "runs": []}


def _prune(index: dict[str, Any], trace_dir: Path) -> None:
    kept: list[dict[str, Any]] = []
    per_agent: dict[str, int] = {}
    runs_sorted = sorted(index["runs"], key=lambda r: r["started_at"], reverse=True)
    for run in runs_sorted:
        agent = run["agent"]
        per_agent.setdefault(agent, 0)
        if per_agent[agent] >= MAX_PER_AGENT or len(kept) >= GLOBAL_CAP:
            _unlink_quiet(trace_dir / f"{run['run_id']}.json")
            continue
        per_agent[agent] += 1
        kept.append(run)
    index["runs"] = kept


def _unlink_quiet(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass
```

Append to `step0-shared/axe_core/__init__.py`:

```python
from axe_core.trace import Tracer  # noqa: E402,F401
```

- [ ] **Step 4: Run tests to confirm pass**

```bash
cd step0-shared && pytest tests/test_trace.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add step0-shared/axe_core/trace.py step0-shared/axe_core/__init__.py step0-shared/tests/test_trace.py
git commit -m "feat(axe_core): add Tracer with atomic index + pruning"
```

---

## Task 3: `axe_core.schemas` — pydantic models for all artifacts

**Files:**
- Create: `step0-shared/axe_core/schemas.py`
- Create: `step0-shared/tests/test_schemas.py`

Freeze the data contracts from spec §5 in pydantic models so every writer validates on save and every reader (FastAPI, test fixtures) can parse into typed objects. Models mirror the JSON shapes exactly — extra fields allowed on existing files so we don't break old data.

- [ ] **Step 1: Add pydantic dependency and write failing tests**

Edit `step0-shared/pyproject.toml` — already lists `pydantic>=2.6`, confirm present.

Create `step0-shared/tests/test_schemas.py`:

```python
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from axe_core.schemas import (
    AlphaReport,
    DecisionLogEntry,
    HealthReport,
    NewsItem,
    NewsReport,
    TraceIndex,
    TraceIndexRun,
)


def test_alpha_report_parses_spec_example():
    payload = {
        "report_date": "2026-04-12",
        "generated_at": "2026-04-12T01:59:31+03:00",
        "top_opportunities": [
            {
                "ticker": "RTX",
                "opportunity_type": "earnings_drift",
                "thesis": "thesis text",
                "conviction_score": 7,
                "trigger_source": "yfinance_earnings",
                "trigger_data_point": "dp",
                "why_retail_is_missing_this": "why",
                "risk_flags": "rf",
                "raw_facts": {"k": "v"},
                "base_score": 6.9,
            }
        ],
    }
    report = AlphaReport.model_validate(payload)
    assert report.top_opportunities[0].ticker == "RTX"
    assert report.top_opportunities[0].conviction_score == 7


def test_news_item_rejects_impact_score_below_6():
    item = {
        "id": "abc",
        "title": "t",
        "url": "https://x",
        "source": "reuters",
        "published_at": "2026-04-15T08:41:00Z",
        "tickers_mentioned": ["MSFT"],
        "portfolio_relevance": "held",
        "impact_score": 5,
        "impact_rationale": "r",
        "decision_hook": None,
        "scored_by": "claude-haiku-4-5",
    }
    with pytest.raises(ValidationError):
        NewsItem.model_validate(item)


def test_news_item_accepts_valid():
    item = {
        "id": "abc",
        "title": "t",
        "url": "https://x",
        "source": "reuters",
        "published_at": "2026-04-15T08:41:00Z",
        "tickers_mentioned": ["MSFT"],
        "portfolio_relevance": "held",
        "impact_score": 7,
        "impact_rationale": "r",
        "decision_hook": None,
        "scored_by": "claude-haiku-4-5",
    }
    NewsItem.model_validate(item)


def test_news_report_validates_list():
    payload = {
        "generated_at": "2026-04-15T09:00:00Z",
        "sources_polled": ["reuters-biz"],
        "items_in": 100,
        "items_kept": 0,
        "items": [],
    }
    NewsReport.model_validate(payload)


def test_trace_index_shape():
    idx = TraceIndex.model_validate(
        {
            "generated_at": "2026-04-15T09:02:00Z",
            "retention": {"max_runs_per_agent": 50, "total_cap": 500},
            "runs": [
                {
                    "run_id": "alpha-15-04-2026T09-00-00Z",
                    "agent": "axe_alpha",
                    "started_at": "2026-04-15T09:00:00Z",
                    "ended_at": "2026-04-15T09:01:34Z",
                    "duration_ms": 94000,
                    "status": "success",
                    "event_count": 28,
                    "summary": "s",
                    "artifact_written": "alpha-latest.json",
                }
            ],
        }
    )
    assert idx.runs[0].status == "success"
    assert isinstance(idx.runs[0], TraceIndexRun)


def test_decision_log_entry_tolerates_legacy_missing_fields():
    # Old entries may lack decision_type/tags; must still parse.
    DecisionLogEntry.model_validate(
        {"ts": "2026-01-01T00:00:00Z", "ticker": "MSFT", "note": "legacy entry"}
    )


def test_health_report_thresholds():
    hr = HealthReport.model_validate(
        {
            "generated_at": "2026-04-15T09:02:00Z",
            "artifacts": {
                "portfolio": {
                    "last_refresh": "2026-04-15T08:00:00Z",
                    "age_min": 62,
                    "status": "fresh",
                }
            },
            "freshness_thresholds_min": {"portfolio": 240, "alpha": 1440, "news": 60},
        }
    )
    assert hr.freshness_thresholds_min["portfolio"] == 240
```

- [ ] **Step 2: Run tests, confirm failure**

```bash
cd step0-shared && pytest tests/test_schemas.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'axe_core.schemas'`.

- [ ] **Step 3: Implement `schemas.py`**

Create `step0-shared/axe_core/schemas.py`:

```python
"""Pydantic models for all JSON artifacts in step6-dashboard/public/."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow")


# --- Alpha (§5.1) ---

class AlphaOpportunity(_Base):
    ticker: str
    opportunity_type: str
    thesis: str
    conviction_score: int = Field(ge=0, le=10)
    trigger_source: str
    trigger_data_point: str
    why_retail_is_missing_this: str
    risk_flags: str
    raw_facts: dict[str, Any]
    base_score: float


class AlphaReport(_Base):
    report_date: str
    generated_at: str
    top_opportunities: list[AlphaOpportunity]


# --- News (§5.2) ---

PortfolioRelevance = Literal["held", "watchlist", "sector", "none"]


class NewsItem(_Base):
    id: str
    title: str
    url: str
    source: str
    published_at: str
    tickers_mentioned: list[str]
    portfolio_relevance: PortfolioRelevance
    impact_score: int = Field(ge=6, le=10)
    impact_rationale: str
    decision_hook: str | None = None
    scored_by: str


class NewsReport(_Base):
    generated_at: str
    sources_polled: list[str]
    items_in: int
    items_kept: int
    items: list[NewsItem]


# --- Trace index (§5.4) ---

TraceStatus = Literal["success", "failed", "partial"]


class TraceIndexRun(_Base):
    run_id: str
    agent: str
    started_at: str
    ended_at: str
    duration_ms: int
    status: TraceStatus
    event_count: int
    summary: str
    artifact_written: str | None = None


class TraceIndex(_Base):
    generated_at: str
    retention: dict[str, int]
    runs: list[TraceIndexRun]


# --- Decision log (§5.5) ---

DecisionType = Literal["enter", "exit", "trim", "add", "hold", "note"]


class DecisionLogEntry(_Base):
    # All fields optional — legacy entries may be missing most of them.
    ts: str | None = None
    ticker: str | None = None
    decision_type: DecisionType | None = None
    tags: list[str] | None = None
    note: str | None = None


# --- Health (§5.6) ---

ArtifactStatus = Literal["fresh", "stale", "missing"]


class ArtifactHealth(_Base):
    last_refresh: str | None = None
    age_min: int | None = None
    status: ArtifactStatus


class HealthReport(_Base):
    generated_at: str
    artifacts: dict[str, ArtifactHealth]
    freshness_thresholds_min: dict[str, int]
```

Append re-exports to `step0-shared/axe_core/__init__.py`:

```python
from axe_core.schemas import (  # noqa: E402,F401
    AlphaOpportunity,
    AlphaReport,
    ArtifactHealth,
    DecisionLogEntry,
    HealthReport,
    NewsItem,
    NewsReport,
    TraceIndex,
    TraceIndexRun,
)
```

- [ ] **Step 4: Run tests to confirm pass**

```bash
cd step0-shared && pytest tests/test_schemas.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Run full suite as regression check**

```bash
cd step0-shared && pytest -v
```

Expected: all tests (paths + trace + schemas) pass.

- [ ] **Step 6: Commit**

```bash
git add step0-shared/axe_core/schemas.py step0-shared/axe_core/__init__.py step0-shared/tests/test_schemas.py
git commit -m "feat(axe_core): freeze data contracts as pydantic schemas"
```

---

## Task 4: Wire `Tracer` into `axe_alpha` + copy report to `alpha-latest.json`

**Files:**
- Modify: `step4-alpha-hunter/pyproject.toml` (add `axe-core` dep)
- Modify: `step4-alpha-hunter/axe_alpha/cli.py:1-22` (wrap main in Tracer, write alpha-latest.json)
- Create: `step4-alpha-hunter/tests/__init__.py`
- Create: `step4-alpha-hunter/tests/test_cli_trace.py`

Every alpha run must emit a trace file and refresh `step6-dashboard/public/alpha-latest.json`. We keep the existing dated report write untouched (archival), and add the two new side-effects around it.

- [ ] **Step 1: Add `axe-core` to alpha's dependencies**

Edit `step4-alpha-hunter/pyproject.toml`, replace dependencies block:

```toml
dependencies = [
  "axe-core",
  "httpx>=0.27",
  "python-dotenv>=1.0",
  "yfinance>=0.2.50",
  "ddgs>=9.5.0",
  "pandas>=2.2",
  "playwright>=1.52.0",
]

[tool.uv.sources]
axe-core = { path = "../step0-shared", editable = true }
```

Install:

```bash
cd step4-alpha-hunter && pip install -e . -e ../step0-shared
```

- [ ] **Step 2: Write failing test for traced CLI**

Create `step4-alpha-hunter/tests/__init__.py` (empty file).

Create `step4-alpha-hunter/tests/test_cli_trace.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from axe_alpha import cli as alpha_cli
from axe_core import trace as trace_mod


def _fake_report() -> dict:
    return {
        "report_date": "2026-04-15",
        "generated_at": "2026-04-15T09:00:00Z",
        "top_opportunities": [
            {
                "ticker": "RTX",
                "opportunity_type": "earnings_drift",
                "thesis": "x",
                "conviction_score": 7,
                "trigger_source": "yfinance_earnings",
                "trigger_data_point": "d",
                "why_retail_is_missing_this": "w",
                "risk_flags": "r",
                "raw_facts": {},
                "base_score": 6.9,
            }
        ],
    }


def test_cli_emits_trace_and_writes_alpha_latest(tmp_path, monkeypatch):
    # Redirect public dir to tmp.
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)
    monkeypatch.setattr(alpha_cli, "public_dir", lambda: tmp_path)

    # Stub archival path to a tmp location.
    archive = tmp_path / "archive" / "2026-04-15.json"
    monkeypatch.setattr(alpha_cli, "report_path_for_date", lambda d: archive)

    # Stub env + network.
    monkeypatch.setattr(alpha_cli, "load_project_env", lambda: None)
    monkeypatch.setattr(alpha_cli, "openai_api_key", lambda: "sk-test")

    async def fake_run(api_key):
        return _fake_report()

    monkeypatch.setattr(alpha_cli, "run_alpha_hunter_scan", fake_run)

    alpha_cli.main()

    # alpha-latest.json written
    latest = json.loads((tmp_path / "alpha-latest.json").read_text())
    assert latest["report_date"] == "2026-04-15"
    # Archive also written
    assert archive.exists()
    # Trace file and index exist
    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert len(index["runs"]) == 1
    assert index["runs"][0]["agent"] == "axe_alpha"
    assert index["runs"][0]["artifact_written"] == "alpha-latest.json"
    assert index["runs"][0]["status"] == "success"


def test_cli_records_failure_in_trace(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)
    monkeypatch.setattr(alpha_cli, "public_dir", lambda: tmp_path)
    monkeypatch.setattr(alpha_cli, "load_project_env", lambda: None)
    monkeypatch.setattr(alpha_cli, "openai_api_key", lambda: "sk-test")

    async def boom(api_key):
        raise RuntimeError("upstream down")

    monkeypatch.setattr(alpha_cli, "run_alpha_hunter_scan", boom)

    try:
        alpha_cli.main()
    except RuntimeError:
        pass

    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert index["runs"][0]["status"] == "failed"
```

- [ ] **Step 3: Run tests, confirm failure**

```bash
cd step4-alpha-hunter && pytest tests/test_cli_trace.py -v
```

Expected: FAIL — `alpha-latest.json` not written, no trace emitted.

- [ ] **Step 4: Rewrite `axe_alpha/cli.py`**

Replace the entire contents of `step4-alpha-hunter/axe_alpha/cli.py` (lines 1-22) with:

```python
from __future__ import annotations

import asyncio
import json

from axe_alpha.alpha_scan import report_path_for_date, run_alpha_hunter_scan
from axe_alpha.util import load_project_env, openai_api_key
from axe_core import Tracer
from axe_core.paths import public_dir


def main() -> None:
    load_project_env()
    api_key = openai_api_key()

    tracer = Tracer(agent="axe_alpha")
    tracer.start()
    tracer.event(step="load_env", thought="env loaded, key resolved")

    try:
        tracer.event(step="scan", thought="running alpha hunter scan")
        report = asyncio.run(run_alpha_hunter_scan(api_key=api_key))
    except Exception as exc:
        tracer.event(step="error", thought=f"scan failed: {exc}")
        tracer.finalize(status="failed", summary=f"scan failed: {exc}", artifact_written=None)
        raise

    report_date = report["report_date"]
    n_opps = len(report.get("top_opportunities", []))

    archive_path = report_path_for_date(report_date)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    latest = public_dir() / "alpha-latest.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    tmp = latest.with_name("alpha-latest.json.tmp")
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(latest)

    tracer.event(
        step="write_artifacts",
        thought=f"wrote archive {archive_path.name} and alpha-latest.json",
        io={"out": {"opportunities": n_opps}},
    )
    tracer.finalize(
        status="success",
        summary=f"scanned and surfaced {n_opps} opportunities",
        artifact_written="alpha-latest.json",
    )

    print(json.dumps({"report_path": str(archive_path), "latest": str(latest), **report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to confirm pass**

```bash
cd step4-alpha-hunter && pytest tests/test_cli_trace.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Smoke-test against fixture (no network)**

```bash
cd step4-alpha-hunter && pytest -v
```

Expected: full package test run passes (2+ tests, no regressions).

- [ ] **Step 7: Commit**

```bash
git add step4-alpha-hunter/pyproject.toml step4-alpha-hunter/axe_alpha/cli.py step4-alpha-hunter/tests/
git commit -m "feat(axe_alpha): emit trace + write alpha-latest.json on every run"
```

---

## Task 5: Wire `Tracer` into `axe_portfolio`

**Files:**
- Modify: `step5-portfolio-tracking/pyproject.toml` (add `axe-core` dep)
- Modify: `step5-portfolio-tracking/axe_portfolio/cli.py:1-22` (wrap `main` in Tracer)
- Create: `step5-portfolio-tracking/tests/__init__.py`
- Create: `step5-portfolio-tracking/tests/test_cli_trace.py`

`axe_portfolio` already writes `portfolio.json` via `run_portfolio_review()`. We add a Tracer around the CLI so Panel 5 (Agent Status) can show portfolio runs alongside alpha/news. We do NOT touch `tracker.py` — the CLI is the observation boundary.

- [ ] **Step 1: Add `axe-core` dependency**

Edit `step5-portfolio-tracking/pyproject.toml` — locate the `dependencies = [ ... ]` block and add `"axe-core",` as the first entry, then append at the bottom of the file:

```toml
[tool.uv.sources]
axe-core = { path = "../step0-shared", editable = true }
```

Install:

```bash
cd step5-portfolio-tracking && pip install -e . -e ../step0-shared
```

- [ ] **Step 2: Write failing test**

Create `step5-portfolio-tracking/tests/__init__.py` (empty).

Create `step5-portfolio-tracking/tests/test_cli_trace.py`:

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

- [ ] **Step 3: Run tests, confirm failure**

```bash
cd step5-portfolio-tracking && pytest tests/test_cli_trace.py -v
```

Expected: FAIL — no trace emitted.

- [ ] **Step 4: Rewrite `axe_portfolio/cli.py`**

Replace the entire contents of `step5-portfolio-tracking/axe_portfolio/cli.py` (lines 1-22) with:

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

    print(json.dumps({
        "normalized_csv_path": str(artifacts.normalized_csv_path),
        "weekly_review_path": str(artifacts.weekly_review_path),
        "position_table": artifacts.position_table,
        "unified_sector_allocation": artifacts.unified_sector_allocation,
        "spy_comparison": artifacts.spy_comparison,
        "hishtalmut_status": artifacts.hishtalmut_status,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to confirm pass**

```bash
cd step5-portfolio-tracking && pytest tests/test_cli_trace.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Run full package test suite**

```bash
cd step5-portfolio-tracking && pytest -v
```

Expected: all tests pass, no regressions.

- [ ] **Step 7: Commit**

```bash
git add step5-portfolio-tracking/pyproject.toml step5-portfolio-tracking/axe_portfolio/cli.py step5-portfolio-tracking/tests/
git commit -m "feat(axe_portfolio): emit trace on every review run"
```

---

## Task 6: `axe_orchestrator` CLI skeleton — `run alpha|news|portfolio|all`

**Files:**
- Create: `step7-automation/pyproject.toml`
- Create: `step7-automation/axe_orchestrator/__init__.py`
- Create: `step7-automation/axe_orchestrator/cli.py`
- Create: `step7-automation/axe_orchestrator/runners.py`
- Create: `step7-automation/tests/__init__.py`
- Create: `step7-automation/tests/test_cli.py`

One CLI that dispatches to each agent. Today it shells out to the existing per-agent entrypoints; later (Week 4) FastAPI wraps this same module. Exit code = failure count across runs. `run all` always runs every agent even if one fails.

- [ ] **Step 1: Create `pyproject.toml`**

Create `step7-automation/pyproject.toml`:

```toml
[project]
name = "axe-orchestrator"
version = "0.1.0"
description = "Axe Capital orchestrator CLI (and future FastAPI backend)"
requires-python = ">=3.11"
dependencies = ["axe-core"]

[project.optional-dependencies]
test = ["pytest>=8.0"]
api = ["fastapi>=0.110", "uvicorn>=0.29", "sse-starlette>=2.0"]

[project.scripts]
axe = "axe_orchestrator.cli:main"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["axe_orchestrator*"]

[tool.uv.sources]
axe-core = { path = "../step0-shared", editable = true }
```

Install:

```bash
cd step7-automation && pip install -e .[test] -e ../step0-shared
```

- [ ] **Step 2: Write failing tests**

Create `step7-automation/tests/__init__.py` (empty).

Create `step7-automation/tests/test_cli.py`:

```python
from __future__ import annotations

from axe_orchestrator import cli, runners


def test_run_alpha_calls_alpha_runner(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(runners, "run_alpha", lambda: calls.append("alpha") or 0)
    exit_code = cli.main(["run", "alpha"])
    assert calls == ["alpha"]
    assert exit_code == 0


def test_run_all_invokes_every_agent_even_if_one_fails(monkeypatch):
    order = []

    def ok(name):
        def _r():
            order.append(name)
            return 0
        return _r

    def bad(name):
        def _r():
            order.append(name)
            return 1
        return _r

    monkeypatch.setattr(runners, "run_portfolio", ok("portfolio"))
    monkeypatch.setattr(runners, "run_alpha", bad("alpha"))
    monkeypatch.setattr(runners, "run_news", ok("news"))

    exit_code = cli.main(["run", "all"])

    assert order == ["portfolio", "alpha", "news"]
    assert exit_code == 1  # one failure bubbles up


def test_unknown_target_returns_nonzero(monkeypatch, capsys):
    assert cli.main(["run", "bogus"]) != 0


def test_runners_shell_out(monkeypatch):
    captured = {}

    def fake_run(cmd, check, cwd):
        captured["cmd"] = cmd
        captured["cwd"] = str(cwd)
        class R:
            returncode = 0
        return R()

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)
    assert runners.run_alpha() == 0
    assert captured["cmd"][0:2] == ["python", "-m"]
    assert "axe_alpha.cli" in captured["cmd"][2]
```

- [ ] **Step 3: Run tests, confirm failure**

```bash
cd step7-automation && pytest -v
```

Expected: FAIL — modules don't exist.

- [ ] **Step 4: Implement `runners.py`**

Create `step7-automation/axe_orchestrator/__init__.py`:

```python
"""axe_orchestrator — single entrypoint for all agent runs."""
```

Create `step7-automation/axe_orchestrator/runners.py`:

```python
"""Thin wrappers that invoke each agent's CLI. Return codes are failure counts."""
from __future__ import annotations

import subprocess

from axe_core.paths import project_root


def _run_module(module: str, cwd_subdir: str) -> int:
    cwd = project_root() / cwd_subdir
    result = subprocess.run(
        ["python", "-m", module],
        check=False,
        cwd=cwd,
    )
    return 0 if result.returncode == 0 else 1


def run_alpha() -> int:
    return _run_module("axe_alpha.cli", "step4-alpha-hunter")


def run_portfolio() -> int:
    return _run_module("axe_portfolio.cli", "step5-portfolio-tracking")


def run_news() -> int:
    # Placeholder until Task 7 ships axe_news.
    return _run_module("axe_news.cli", "step2-news")
```

- [ ] **Step 5: Implement `cli.py`**

Create `step7-automation/axe_orchestrator/cli.py`:

```python
"""`axe` CLI: axe run alpha|news|portfolio|all"""
from __future__ import annotations

import argparse
import sys

from axe_orchestrator import runners

TARGETS = {
    "alpha": runners.run_alpha,
    "news": runners.run_news,
    "portfolio": runners.run_portfolio,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="axe")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="Run an agent")
    run.add_argument("target", choices=list(TARGETS.keys()) + ["all"])

    args = parser.parse_args(argv)

    if args.cmd != "run":
        parser.error(f"unknown command: {args.cmd}")
        return 2

    if args.target == "all":
        failures = 0
        for name in ("portfolio", "alpha", "news"):
            rc = TARGETS[name]()
            print(f"[axe] {name} -> rc={rc}")
            if rc != 0:
                failures += 1
        return 0 if failures == 0 else 1

    return TARGETS[args.target]()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run tests to confirm pass**

```bash
cd step7-automation && pytest -v
```

Expected: 4 passed.

- [ ] **Step 7: Verify the CLI is discoverable**

```bash
axe run alpha --help 2>&1 | head -5 || python -m axe_orchestrator.cli run alpha --help 2>&1 | head -5
```

Expected: argparse usage banner for `axe run`.

- [ ] **Step 8: Commit**

```bash
git add step7-automation/pyproject.toml step7-automation/axe_orchestrator/ step7-automation/tests/
git commit -m "feat(axe_orchestrator): CLI skeleton with run {alpha,news,portfolio,all}"
```

---

## Task 7: Panel 2 (Targets) — finalize avg-cost-vs-last semantics

**Files:**
- Read: `step6-dashboard/public/targets.json` (fixture — do not modify)
- Modify: `step6-dashboard/src/components/TargetsPanel.jsx`

Spec §6 row 2 says the Targets panel must make the two distance metrics unambiguous: "% from avg cost" vs "% from last". Today the panel renders one number with no label. This task clarifies the UI so Robert can tell at a glance which reference the percentage is measured from. Dashboard has no unit tests — verification is manual in the dev server against `targets.json`.

- [ ] **Step 1: Inspect current behavior**

Read `step6-dashboard/src/components/TargetsPanel.jsx` in full. Locate where the percentage distance is computed and rendered. Read `step6-dashboard/public/targets.json` to identify which fields are available (look for `avg_cost`, `last_price`, `target_price`, or similar).

Note in a scratch doc: which field is currently used for "distance", and whether both `avg_cost` and `last_price` are present on each row.

- [ ] **Step 2: Start dev server for baseline screenshot**

```bash
cd step6-dashboard && npm run dev
```

Open the URL printed (usually `http://localhost:5173`), navigate to the Targets panel, and take note of the current distance column(s). This is the before-state.

- [ ] **Step 3: Edit `TargetsPanel.jsx` — render two explicit columns**

In `step6-dashboard/src/components/TargetsPanel.jsx`, update the table header and rows so each target shows two distinct columns:

- Column header: `Δ vs avg cost` — value: `((target_price - avg_cost) / avg_cost) * 100`, formatted as `+X.X%` / `-X.X%`, green when positive, red when negative, gray when `avg_cost` is missing.
- Column header: `Δ vs last` — value: `((target_price - last_price) / last_price) * 100`, same formatting and color rules.

Concrete implementation pattern (adapt to the file's existing table JSX):

```jsx
function pct(target, ref) {
  if (ref == null || ref === 0 || target == null) return null;
  return ((target - ref) / ref) * 100;
}

function PctCell({ value }) {
  if (value == null) return <td className="text-gray-500">—</td>;
  const sign = value >= 0 ? "+" : "";
  const color = value >= 0 ? "text-green-600" : "text-red-600";
  return <td className={color}>{`${sign}${value.toFixed(1)}%`}</td>;
}

// In the row:
<PctCell value={pct(row.target_price, row.avg_cost)} />
<PctCell value={pct(row.target_price, row.last_price)} />
```

Update the `<thead>` to include both column titles: `Δ vs avg cost` and `Δ vs last`.

If the current file mixes the two into a single `distance` field, remove that field from the row rendering — the two new cells replace it.

- [ ] **Step 4: Manually verify in the dev server**

Reload `http://localhost:5173`, navigate to Targets. Confirm:

1. Two columns appear with headers `Δ vs avg cost` and `Δ vs last`.
2. For a row where `avg_cost` differs from `last_price` (pick any row in `targets.json` where they differ), the two percentages are visibly different.
3. Positive numbers render green with `+`, negative red with `-`.
4. Rows missing `avg_cost` show `—` in the first column but still render the second.
5. No console errors in the browser devtools.

- [ ] **Step 5: Lint**

```bash
cd step6-dashboard && npm run lint
```

Expected: clean. Fix any new warnings introduced by the edit.

- [ ] **Step 6: Commit**

```bash
git add step6-dashboard/src/components/TargetsPanel.jsx
git commit -m "feat(dashboard): split target distance into Δ vs avg cost and Δ vs last"
```

---

## Task 8: Panel 3 — Alpha Opportunities (replaces RiskPanel)

**Files:**
- Delete: `step6-dashboard/src/components/RiskPanel.jsx`
- Create: `step6-dashboard/src/components/AlphaPanel.jsx`
- Modify: `step6-dashboard/src/App.jsx` (swap import + usage)

Spec §6 row 3: delete Risk, build Alpha. Panel reads `alpha-latest.json` (written by Task 4) and renders each opportunity as an expandable card: headline (ticker + type + conviction chip), thesis, "why retail misses this", trigger, risk flags, raw facts. Risk metrics that used to live here folded into Panel 1 in a later iteration — not this task.

- [ ] **Step 1: Read existing `App.jsx` to understand panel wiring**

Read `step6-dashboard/src/App.jsx` to find where `RiskPanel` is imported and rendered. Note the surrounding JSX so the replacement preserves layout and section ordering.

Read `step6-dashboard/public/alpha-latest.json` if present (Task 4 produces it). If the file doesn't exist yet, seed a fixture so manual verification has data:

```bash
cat > step6-dashboard/public/alpha-latest.json <<'EOF'
{
  "report_date": "2026-04-15",
  "generated_at": "2026-04-15T09:00:00Z",
  "top_opportunities": [
    {
      "ticker": "RTX",
      "opportunity_type": "earnings_drift",
      "thesis": "Raytheon's last print beat on margins but the stock drifted sideways. Defense backlog growth not yet reflected in multiples.",
      "conviction_score": 7,
      "trigger_source": "yfinance_earnings",
      "trigger_data_point": "Q1 EPS beat by 8%, revenue in-line, guide raised",
      "why_retail_is_missing_this": "Defense stocks lag tech narrative in social feeds; margin expansion is not a meme.",
      "risk_flags": "Budget continuing resolution risk; FX headwinds in 2H.",
      "raw_facts": {"eps_actual": 1.50, "eps_estimate": 1.39},
      "base_score": 6.9
    },
    {
      "ticker": "ASML",
      "opportunity_type": "insider_cluster",
      "thesis": "Three insiders bought in open market within 5 days at ~€650, cluster size $4.2M.",
      "conviction_score": 8,
      "trigger_source": "sec_form4_cluster",
      "trigger_data_point": "3 insiders, $4.2M, 11-14 Apr 2026",
      "why_retail_is_missing_this": "Form 4 signal buried under daily noise; cluster detection requires tooling.",
      "risk_flags": "China export control overhang unchanged.",
      "raw_facts": {"cluster_count": 3, "cluster_value_usd": 4200000},
      "base_score": 7.4
    }
  ]
}
EOF
```

- [ ] **Step 2: Create `AlphaPanel.jsx`**

Create `step6-dashboard/src/components/AlphaPanel.jsx`:

```jsx
import { useEffect, useState } from "react";

function convictionColor(score) {
  if (score >= 8) return "bg-green-600 text-white";
  if (score >= 6) return "bg-yellow-500 text-black";
  return "bg-gray-400 text-white";
}

function OpportunityCard({ opp }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-200 rounded-lg p-4 mb-3 bg-white">
      <button
        className="w-full flex items-center justify-between text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-center gap-3">
          <span className="font-mono text-lg font-bold">{opp.ticker}</span>
          <span className="text-sm text-gray-600">{opp.opportunity_type}</span>
          <span className={`text-xs px-2 py-0.5 rounded ${convictionColor(opp.conviction_score)}`}>
            conviction {opp.conviction_score}/10
          </span>
        </div>
        <span className="text-gray-400">{open ? "▾" : "▸"}</span>
      </button>
      <p className="mt-2 text-sm text-gray-800">{opp.thesis}</p>
      {open && (
        <div className="mt-3 space-y-2 text-sm">
          <div><span className="font-semibold">Trigger:</span> {opp.trigger_source} — {opp.trigger_data_point}</div>
          <div><span className="font-semibold">Why retail misses this:</span> {opp.why_retail_is_missing_this}</div>
          <div><span className="font-semibold">Risk flags:</span> {opp.risk_flags}</div>
          <details className="mt-2">
            <summary className="cursor-pointer text-gray-600">Raw facts</summary>
            <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto">
              {JSON.stringify(opp.raw_facts, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default function AlphaPanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/alpha-latest.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Alpha Opportunities</h2><p className="text-red-600">Failed to load: {error}</p></section>;
  if (!data) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Alpha Opportunities</h2><p className="text-gray-500">Loading…</p></section>;

  const opps = data.top_opportunities || [];

  return (
    <section className="p-4">
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-xl font-bold">Alpha Opportunities</h2>
        <span className="text-xs text-gray-500">
          {opps.length} opportunities · {data.generated_at}
        </span>
      </div>
      {opps.length === 0 ? (
        <p className="text-gray-500">No opportunities in latest scan.</p>
      ) : (
        opps.map((opp) => <OpportunityCard key={opp.ticker} opp={opp} />)
      )}
    </section>
  );
}
```

- [ ] **Step 3: Swap the panel in `App.jsx`**

Edit `step6-dashboard/src/App.jsx`:

1. Remove the `import RiskPanel from "./components/RiskPanel.jsx";` line.
2. Add `import AlphaPanel from "./components/AlphaPanel.jsx";` near the other panel imports.
3. Replace the JSX element `<RiskPanel ... />` (wherever it appears) with `<AlphaPanel />`.

- [ ] **Step 4: Delete `RiskPanel.jsx`**

```bash
git rm step6-dashboard/src/components/RiskPanel.jsx
```

- [ ] **Step 5: Start dev server and manually verify**

```bash
cd step6-dashboard && npm run dev
```

Open the printed URL. Confirm:

1. A panel titled "Alpha Opportunities" appears where Risk used to be.
2. Header shows "N opportunities · <generated_at>".
3. Each card shows ticker (mono bold), opportunity type, conviction chip (green ≥8, yellow 6-7, gray <6), thesis paragraph.
4. Clicking a card toggles expansion to reveal trigger / why-retail-misses / risk / raw facts (details summary).
5. No console errors in devtools; network tab shows `/alpha-latest.json` 200.

- [ ] **Step 6: Test the error path**

Temporarily rename the fixture:

```bash
mv step6-dashboard/public/alpha-latest.json step6-dashboard/public/alpha-latest.json.bak
```

Reload. The panel must render "Failed to load: HTTP 404" in red, not crash the whole app. Then restore:

```bash
mv step6-dashboard/public/alpha-latest.json.bak step6-dashboard/public/alpha-latest.json
```

- [ ] **Step 7: Lint**

```bash
cd step6-dashboard && npm run lint
```

Expected: clean.

- [ ] **Step 8: Commit**

```bash
git add step6-dashboard/src/components/AlphaPanel.jsx step6-dashboard/src/App.jsx step6-dashboard/public/alpha-latest.json
git rm --cached step6-dashboard/src/components/RiskPanel.jsx 2>/dev/null || true
git commit -m "feat(dashboard): replace Risk panel with Alpha Opportunities"
```

---

## Task 9: Panel 7 — Decision Archive (merge + delete Runbook)

**Files:**
- Delete: `step6-dashboard/src/components/RunbookPanel.jsx`
- Modify: `step6-dashboard/src/components/DecisionLogPanel.jsx` → rename to `DecisionArchivePanel.jsx`
- Modify: `step6-dashboard/src/App.jsx` (imports + usage)
- Read: `step6-dashboard/public/decision-log.jsonl`

Spec §6 row 7: merge DecisionLog + Runbook into one archive; delete Runbook. Archive reads `decision-log.jsonl`, supports text-search across ticker/note/tags, and filters by `decision_type` (spec §5.5 — optional field, so filter chips include an "unspecified" bucket). Each entry is expandable and will later link to the trace that produced it (Task 14).

- [ ] **Step 1: Rename and clear the old component**

```bash
git mv step6-dashboard/src/components/DecisionLogPanel.jsx step6-dashboard/src/components/DecisionArchivePanel.jsx
```

Read the renamed file to understand existing JSONL parsing logic — preserve the parser, replace the render layer.

Read the first ~20 lines of `step6-dashboard/public/decision-log.jsonl` to confirm actual field names (spec says `decision_type`, `tags`, but legacy entries may use other keys). Note any legacy fields (e.g. `ticker`, `note`, `ts`) so the search covers them.

- [ ] **Step 2: Rewrite `DecisionArchivePanel.jsx`**

Replace the body of `step6-dashboard/src/components/DecisionArchivePanel.jsx` with:

```jsx
import { useEffect, useMemo, useState } from "react";

const DECISION_TYPES = ["enter", "exit", "trim", "add", "hold", "note"];

function parseJsonl(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

function typeChip(type) {
  const colors = {
    enter: "bg-green-600 text-white",
    add: "bg-green-400 text-black",
    exit: "bg-red-600 text-white",
    trim: "bg-orange-500 text-white",
    hold: "bg-gray-400 text-white",
    note: "bg-blue-400 text-white",
  };
  return colors[type] || "bg-gray-200 text-gray-700";
}

function EntryRow({ entry }) {
  const [open, setOpen] = useState(false);
  const type = entry.decision_type || "unspecified";
  return (
    <div className="border-b border-gray-100 py-2">
      <button className="w-full text-left flex items-center gap-3" onClick={() => setOpen((v) => !v)}>
        <span className="text-xs text-gray-500 font-mono w-40 shrink-0">{entry.ts || "—"}</span>
        <span className="font-mono font-bold w-16 shrink-0">{entry.ticker || "—"}</span>
        <span className={`text-xs px-2 py-0.5 rounded ${typeChip(type)} shrink-0`}>{type}</span>
        <span className="text-sm text-gray-700 truncate flex-1">{entry.note || entry.summary || ""}</span>
      </button>
      {open && (
        <div className="ml-40 mt-2 text-sm space-y-1">
          {entry.tags?.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {entry.tags.map((t) => (
                <span key={t} className="text-xs bg-gray-100 px-2 py-0.5 rounded">{t}</span>
              ))}
            </div>
          )}
          <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto">{JSON.stringify(entry, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default function DecisionArchivePanel() {
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");
  const [activeType, setActiveType] = useState("all");

  useEffect(() => {
    fetch("/decision-log.jsonl")
      .then((r) => (r.ok ? r.text() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((text) => setEntries(parseJsonl(text)))
      .catch((e) => setError(e.message));
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return entries
      .filter((e) => {
        if (activeType === "all") return true;
        if (activeType === "unspecified") return !e.decision_type;
        return e.decision_type === activeType;
      })
      .filter((e) => {
        if (!q) return true;
        const hay = [
          e.ticker,
          e.note,
          e.summary,
          e.decision_type,
          ...(e.tags || []),
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        return hay.includes(q);
      })
      .sort((a, b) => (b.ts || "").localeCompare(a.ts || ""));
  }, [entries, query, activeType]);

  if (error) {
    return (
      <section className="p-4">
        <h2 className="text-xl font-bold mb-2">Decision Archive</h2>
        <p className="text-red-600">Failed to load: {error}</p>
      </section>
    );
  }

  return (
    <section className="p-4">
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-xl font-bold">Decision Archive</h2>
        <span className="text-xs text-gray-500">{filtered.length} / {entries.length}</span>
      </div>
      <div className="flex flex-wrap gap-2 items-center mb-3">
        <input
          type="search"
          placeholder="Search ticker, note, tags…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="border rounded px-2 py-1 text-sm flex-1 min-w-[200px]"
        />
        <div className="flex gap-1">
          {["all", ...DECISION_TYPES, "unspecified"].map((t) => (
            <button
              key={t}
              onClick={() => setActiveType(t)}
              className={`text-xs px-2 py-1 rounded ${
                activeType === t ? "bg-black text-white" : "bg-gray-100 text-gray-700"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>
      {filtered.length === 0 ? (
        <p className="text-gray-500 text-sm">No entries match filters.</p>
      ) : (
        filtered.map((e, i) => <EntryRow key={`${e.ts || "x"}-${i}`} entry={e} />)
      )}
    </section>
  );
}
```

- [ ] **Step 3: Update `App.jsx`**

Edit `step6-dashboard/src/App.jsx`:

1. Remove `import RunbookPanel from "./components/RunbookPanel.jsx";`
2. Change `import DecisionLogPanel from "./components/DecisionLogPanel.jsx";` → `import DecisionArchivePanel from "./components/DecisionArchivePanel.jsx";`
3. Replace JSX `<DecisionLogPanel ... />` with `<DecisionArchivePanel />`.
4. Remove the JSX element `<RunbookPanel ... />` wherever it appears.

- [ ] **Step 4: Delete `RunbookPanel.jsx`**

```bash
git rm step6-dashboard/src/components/RunbookPanel.jsx
```

- [ ] **Step 5: Start dev server and manually verify**

```bash
cd step6-dashboard && npm run dev
```

Confirm at the printed URL:

1. A panel titled "Decision Archive" appears; Runbook panel is gone.
2. Filter chips: `all`, `enter`, `exit`, `trim`, `add`, `hold`, `note`, `unspecified`.
3. Header counter shows `filtered / total`.
4. Typing into the search box narrows entries in real-time (check that a query matching a ticker reduces the list).
5. Clicking an entry expands to show tags (if any) and raw JSON.
6. Rows with no `decision_type` are visible under the `unspecified` chip.
7. No console errors.

- [ ] **Step 6: Error-path test**

Temporarily block the JSONL:

```bash
mv step6-dashboard/public/decision-log.jsonl step6-dashboard/public/decision-log.jsonl.bak
```

Reload, confirm "Failed to load: HTTP 404" renders in red without crashing. Restore:

```bash
mv step6-dashboard/public/decision-log.jsonl.bak step6-dashboard/public/decision-log.jsonl
```

- [ ] **Step 7: Lint**

```bash
cd step6-dashboard && npm run lint
```

Expected: clean.

- [ ] **Step 8: Commit**

```bash
git add step6-dashboard/src/components/DecisionArchivePanel.jsx step6-dashboard/src/App.jsx
git commit -m "feat(dashboard): merge Decision Log + Runbook into Decision Archive"
```

---

## Task 10: `axe_news` — scaffold + RSS ingestion with dedup & ticker extraction

**Files:**
- Create: `step2-news/pyproject.toml`
- Create: `step2-news/axe_news/__init__.py`
- Create: `step2-news/axe_news/feeds.py`
- Create: `step2-news/axe_news/ingest.py`
- Create: `step2-news/tests/__init__.py`
- Create: `step2-news/tests/fixtures/sample-reuters.xml`
- Create: `step2-news/tests/test_ingest.py`

Stage 1 of the news pipeline: fetch all configured feeds, parse, dedupe by URL hash, extract tickers. No LLM yet — Task 11 wires the impact scorer on top of this. Scaffold lives at `step2-news/` per spec §4.

- [ ] **Step 1: Create `pyproject.toml`**

Create `step2-news/pyproject.toml`:

```toml
[project]
name = "axe-news"
version = "0.1.0"
description = "Axe Capital Step 2: RSS ingestion + LLM impact scorer"
requires-python = ">=3.11"
dependencies = [
  "axe-core",
  "httpx>=0.27",
  "feedparser>=6.0",
  "python-dotenv>=1.0",
  "anthropic>=0.40",
]

[project.optional-dependencies]
test = ["pytest>=8.0", "pytest-asyncio>=0.23"]

[project.scripts]
axe-news = "axe_news.cli:main"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["axe_news*"]

[tool.uv.sources]
axe-core = { path = "../step0-shared", editable = true }
```

Install:

```bash
mkdir -p step2-news/axe_news step2-news/tests/fixtures
cd step2-news && pip install -e .[test] -e ../step0-shared
```

- [ ] **Step 2: Write the feed catalog**

Create `step2-news/axe_news/__init__.py`:

```python
"""axe_news — RSS + LLM impact scoring."""
```

Create `step2-news/axe_news/feeds.py`:

```python
"""Static catalog of RSS feeds to poll."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Feed:
    id: str       # short stable id used in trace + sources_polled
    url: str
    category: str  # "wire" | "regulatory" | "ticker"


FEEDS: tuple[Feed, ...] = (
    Feed("reuters-biz", "https://feeds.reuters.com/reuters/businessNews", "wire"),
    Feed("bloomberg-mkts", "https://feeds.bloomberg.com/markets/news.rss", "wire"),
    Feed("sec-edgar-8k", "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=8-K&dateb=&owner=include&count=40&output=atom", "regulatory"),
)


def yahoo_ticker_feed(ticker: str) -> Feed:
    return Feed(
        id=f"yahoo-ticker:{ticker}",
        url=f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        category="ticker",
    )
```

- [ ] **Step 3: Add a fixture feed for tests**

Create `step2-news/tests/fixtures/sample-reuters.xml` with a minimal RSS 2.0 payload:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>Reuters Biz (fixture)</title>
  <link>https://reuters.example/biz</link>
  <description>test</description>
  <item>
    <title>MSFT faces new DOJ antitrust probe over AI bundling</title>
    <link>https://reuters.example/msft-antitrust</link>
    <pubDate>Wed, 15 Apr 2026 08:41:00 GMT</pubDate>
    <description>The Department of Justice opened an inquiry into Microsoft and GOOG cloud bundling practices.</description>
  </item>
  <item>
    <title>Analyst raises AAPL price target to $250</title>
    <link>https://reuters.example/aapl-pt</link>
    <pubDate>Wed, 15 Apr 2026 08:30:00 GMT</pubDate>
    <description>Routine price target bump.</description>
  </item>
  <item>
    <title>RTX Q1 earnings beat estimates</title>
    <link>https://reuters.example/rtx-q1</link>
    <pubDate>Wed, 15 Apr 2026 07:00:00 GMT</pubDate>
    <description>Raytheon reported Q1 EPS $1.50 beating $1.39.</description>
  </item>
</channel></rss>
```

- [ ] **Step 4: Write failing tests**

Create `step2-news/tests/__init__.py` (empty).

Create `step2-news/tests/test_ingest.py`:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from axe_news.feeds import Feed
from axe_news.ingest import (
    RawItem,
    dedupe,
    extract_tickers,
    fetch_feed,
    item_id,
    parse_feed_bytes,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_feed_bytes_returns_items():
    raw = (FIXTURES / "sample-reuters.xml").read_bytes()
    feed = Feed("reuters-biz", "https://x", "wire")
    items = parse_feed_bytes(raw, feed)
    assert len(items) == 3
    assert items[0].title.startswith("MSFT faces")
    assert items[0].source == "reuters-biz"
    assert items[0].url == "https://reuters.example/msft-antitrust"


def test_item_id_is_stable_sha1_of_url():
    i1 = RawItem(title="t1", url="https://x", source="s", published_at="2026-04-15T00:00:00Z", summary="")
    i2 = RawItem(title="t2", url="https://x", source="s", published_at="2026-04-15T01:00:00Z", summary="")
    assert item_id(i1) == item_id(i2)
    assert len(item_id(i1)) == 40  # sha1 hex


def test_dedupe_keeps_first_occurrence():
    i1 = RawItem(title="first", url="https://a", source="s", published_at="2026-04-15T00:00:00Z", summary="")
    dup = RawItem(title="dup", url="https://a", source="s2", published_at="2026-04-15T01:00:00Z", summary="")
    i3 = RawItem(title="third", url="https://b", source="s", published_at="2026-04-15T02:00:00Z", summary="")
    out = dedupe([i1, dup, i3])
    assert [it.url for it in out] == ["https://a", "https://b"]


def test_extract_tickers_finds_caps_tokens_from_title_and_summary():
    item = RawItem(
        title="MSFT faces DOJ probe",
        url="https://x",
        source="reuters-biz",
        published_at="2026-04-15T00:00:00Z",
        summary="Microsoft and GOOG cloud bundling. Also mentions AAPL.",
    )
    watchlist = {"MSFT", "GOOG", "AAPL", "RTX", "ASML"}
    tickers = extract_tickers(item, watchlist)
    assert set(tickers) == {"MSFT", "GOOG", "AAPL"}


def test_extract_tickers_ignores_common_english_caps_tokens():
    item = RawItem(
        title="THE CEO OF MSFT WILL SPEAK TODAY",
        url="https://x",
        source="s",
        published_at="2026-04-15T00:00:00Z",
        summary="",
    )
    tickers = extract_tickers(item, {"MSFT"})
    # Common words (THE, CEO, OF, WILL, TODAY) are not in the watchlist, so they're filtered
    assert tickers == ["MSFT"]


@pytest.mark.asyncio
async def test_fetch_feed_uses_httpx_client(monkeypatch):
    raw = (FIXTURES / "sample-reuters.xml").read_bytes()
    feed = Feed("reuters-biz", "https://x", "wire")

    class FakeResp:
        status_code = 200
        content = raw

        def raise_for_status(self):
            pass

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

        async def get(self, url, **kwargs):
            return FakeResp()

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", lambda **k: FakeClient())
    items = await fetch_feed(feed)
    assert len(items) == 3
```

- [ ] **Step 5: Run tests, confirm failure**

```bash
cd step2-news && pytest tests/test_ingest.py -v
```

Expected: FAIL — `axe_news.ingest` does not exist.

- [ ] **Step 6: Implement `ingest.py`**

Create `step2-news/axe_news/ingest.py`:

```python
"""RSS fetch, parse, dedupe, ticker extraction."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

import feedparser
import httpx

from axe_news.feeds import Feed


@dataclass
class RawItem:
    title: str
    url: str
    source: str
    published_at: str
    summary: str


USER_AGENT = "AxeCapitalNews/0.1 (research; contact: roberttiger9@gmail.com)"
TICKER_RE = re.compile(r"\b([A-Z]{2,5})\b")


def item_id(item: RawItem) -> str:
    return hashlib.sha1(item.url.encode("utf-8")).hexdigest()


def _to_iso(entry) -> str:
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None) or entry.get(key) if isinstance(entry, dict) else getattr(entry, key, None)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_feed_bytes(raw: bytes, feed: Feed) -> list[RawItem]:
    parsed = feedparser.parse(raw)
    items: list[RawItem] = []
    for entry in parsed.entries:
        items.append(
            RawItem(
                title=(entry.get("title") or "").strip(),
                url=(entry.get("link") or "").strip(),
                source=feed.id,
                published_at=_to_iso(entry),
                summary=(entry.get("summary") or entry.get("description") or "").strip(),
            )
        )
    return items


async def fetch_feed(feed: Feed, timeout: float = 15.0) -> list[RawItem]:
    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": USER_AGENT}) as client:
        resp = await client.get(feed.url)
        resp.raise_for_status()
        return parse_feed_bytes(resp.content, feed)


def dedupe(items: Iterable[RawItem]) -> list[RawItem]:
    seen: set[str] = set()
    out: list[RawItem] = []
    for item in items:
        key = item_id(item)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def extract_tickers(item: RawItem, watchlist: set[str]) -> list[str]:
    """Extract ALL-CAPS tokens that match the portfolio/watchlist set.

    Restricting to the watchlist avoids false positives on English words
    that happen to be in caps (THE, CEO, NEWS, etc.). Unknown tickers are
    intentionally dropped — the user told us what matters.
    """
    text = f"{item.title} {item.summary}"
    found: list[str] = []
    for token in TICKER_RE.findall(text):
        if token in watchlist and token not in found:
            found.append(token)
    return found
```

- [ ] **Step 7: Run tests to confirm pass**

```bash
cd step2-news && pytest tests/test_ingest.py -v
```

Expected: 6 passed.

- [ ] **Step 8: Commit**

```bash
git add step2-news/pyproject.toml step2-news/axe_news/ step2-news/tests/
git commit -m "feat(axe_news): scaffold package with RSS ingest, dedup, ticker extraction"
```

---

## Task 11: `axe_news` — LLM impact scorer + CLI writes `news-latest.json`

**Files:**
- Create: `step2-news/axe_news/scorer.py`
- Create: `step2-news/axe_news/watchlist.py`
- Create: `step2-news/axe_news/pipeline.py`
- Create: `step2-news/axe_news/cli.py`
- Create: `step2-news/tests/test_scorer.py`
- Create: `step2-news/tests/test_pipeline.py`
- Create: `step2-news/tests/test_cli.py`

Stage 2: score each dedup'd item with Claude Haiku 4.5 (prompt-cached system message), keep items with `impact_score >= 6`, write `news-latest.json` atomically, emit Tracer events. The LLM system prompt enforces spec §5.2 rules: reject analyst ratings / price-targets / generic commentary, keep regulatory / M&A / strategy shifts / exec changes / macro / litigation / supply-chain.

- [ ] **Step 1: Extract watchlist from `INVESTOR_PROFILE.md`**

Create `step2-news/axe_news/watchlist.py`:

```python
"""Resolve the current watchlist (held + interesting tickers) from INVESTOR_PROFILE.md."""
from __future__ import annotations

import re

from axe_core.paths import project_root


def load_watchlist() -> set[str]:
    text = (project_root() / "INVESTOR_PROFILE.md").read_text(encoding="utf-8")
    tickers: set[str] = set()
    in_holdings = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "### IBKR Holdings — Current Positions":
            in_holdings = True
            continue
        if in_holdings and stripped.startswith("**IBKR NAV**"):
            in_holdings = False
        if in_holdings and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells and re.fullmatch(r"[A-Z]{1,5}", cells[0] or ""):
                tickers.add(cells[0])
    # Fallback minimum set if the profile hasn't been parsed yet.
    if not tickers:
        tickers = {"MSFT", "GOOG", "AAPL", "NVDA", "RTX", "ASML", "SPY", "QQQ"}
    return tickers
```

- [ ] **Step 2: Write the scorer tests**

Create `step2-news/tests/test_scorer.py`:

```python
from __future__ import annotations

from axe_news.ingest import RawItem
from axe_news.scorer import ImpactScore, build_prompt, parse_response, score_item


def _item(title="t", summary="s") -> RawItem:
    return RawItem(
        title=title,
        url="https://x",
        source="reuters-biz",
        published_at="2026-04-15T00:00:00Z",
        summary=summary,
    )


def test_build_prompt_includes_item_and_tickers():
    prompt = build_prompt(_item("MSFT antitrust probe"), tickers=["MSFT"])
    assert "MSFT" in prompt
    assert "antitrust" in prompt


def test_parse_response_happy_path():
    raw = '{"impact_score": 8, "impact_rationale": "DOJ probe could force structural remedy", "decision_hook": "Consider trimming MSFT if probe widens", "portfolio_relevance": "held"}'
    out = parse_response(raw)
    assert out == ImpactScore(
        impact_score=8,
        impact_rationale="DOJ probe could force structural remedy",
        decision_hook="Consider trimming MSFT if probe widens",
        portfolio_relevance="held",
    )


def test_parse_response_tolerates_markdown_fence():
    raw = "```json\n{\"impact_score\": 6, \"impact_rationale\": \"r\", \"decision_hook\": null, \"portfolio_relevance\": \"sector\"}\n```"
    out = parse_response(raw)
    assert out.impact_score == 6
    assert out.decision_hook is None


def test_parse_response_returns_none_on_garbage():
    assert parse_response("not json at all") is None


def test_score_item_uses_anthropic_sdk_with_cache_control(monkeypatch):
    calls = {}

    class FakeMessage:
        def __init__(self):
            self.content = [type("B", (), {"text": '{"impact_score": 7, "impact_rationale": "r", "decision_hook": null, "portfolio_relevance": "held"}'})]

    class FakeMessages:
        def create(self, **kwargs):
            calls["kwargs"] = kwargs
            return FakeMessage()

    class FakeClient:
        def __init__(self, *a, **k):
            self.messages = FakeMessages()

    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)

    item = _item("MSFT probe", "DOJ opens inquiry")
    result = score_item(item, tickers=["MSFT"], relevance="held", api_key="sk-test")

    assert result.impact_score == 7
    assert calls["kwargs"]["model"] == "claude-haiku-4-5-20251001"
    # The system block must be marked as cacheable
    system_blocks = calls["kwargs"]["system"]
    assert any(b.get("cache_control", {}).get("type") == "ephemeral" for b in system_blocks)
```

- [ ] **Step 3: Implement `scorer.py`**

Create `step2-news/axe_news/scorer.py`:

```python
"""LLM-based impact scoring using Claude Haiku 4.5 with prompt caching."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

import anthropic

from axe_news.ingest import RawItem

MODEL = "claude-haiku-4-5-20251001"
MODEL_NAME_FOR_ARTIFACT = "claude-haiku-4-5"

PortfolioRelevance = Literal["held", "watchlist", "sector", "none"]

SYSTEM_PROMPT = """You are the impact analyst for Axe Capital, a small personal-investment research shop.

Your job: given one news item, return ONE JSON object scoring whether this item should reach a human investor. No prose outside the JSON.

Schema:
{
  "impact_score": <int 0..10>,
  "impact_rationale": "<1 sentence on why this moves markets or changes a decision>",
  "decision_hook": "<1 sentence action hint OR null>",
  "portfolio_relevance": "held" | "watchlist" | "sector" | "none"
}

Scoring rubric (anchor to 6):
  9-10: Highly likely to change a portfolio decision today (regulatory action on a held name, tender/M&A bid, major guide cut).
  7-8:  Significant strategic shift (regulatory probe opened, exec departure, macro regime change, real supply-chain disruption).
  6:    Credible event worth surfacing; reader should be aware before next decision.
  <=5:  Do not surface. Score below 6 means rejection.

HARD REJECT rules (always score <=5):
- Analyst rating changes
- Price-target changes of any direction
- Routine earnings-preview speculation without hard data
- Generic market commentary / sector recap / "what to watch"
- Conference/event reminders
- Already-reported news with no new info

HARD KEEP rules (lean 7+ unless info is thin):
- Regulatory actions, investigations, enforcement
- M&A announcements, tender offers, rumored bids with sourced detail
- Major product/strategy shifts, platform changes, pricing model changes
- C-suite departures, founder changes, board shake-ups
- Macro/geopolitical events that reshape sector dynamics (rate shocks, export controls)
- Concrete litigation milestones
- Supply-chain disruptions affecting known suppliers/customers of watchlist names

Default to skepticism: if uncertain between 5 and 6, choose 5.
"""


@dataclass
class ImpactScore:
    impact_score: int
    impact_rationale: str
    decision_hook: str | None
    portfolio_relevance: PortfolioRelevance


def build_prompt(item: RawItem, tickers: list[str]) -> str:
    return (
        f"Tickers in watchlist mentioned: {', '.join(tickers) if tickers else '(none)'}\n"
        f"Source: {item.source}\n"
        f"Published: {item.published_at}\n"
        f"Title: {item.title}\n"
        f"Summary: {item.summary}\n"
        f"URL: {item.url}\n\n"
        f"Return the JSON object only."
    )


_FENCE_RE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL)


def parse_response(text: str) -> ImpactScore | None:
    match = _FENCE_RE.search(text)
    payload = match.group(1) if match else text
    try:
        data = json.loads(payload)
        return ImpactScore(
            impact_score=int(data["impact_score"]),
            impact_rationale=str(data["impact_rationale"]),
            decision_hook=data.get("decision_hook"),
            portfolio_relevance=data["portfolio_relevance"],
        )
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def score_item(
    item: RawItem,
    tickers: list[str],
    relevance: PortfolioRelevance,
    api_key: str,
) -> ImpactScore | None:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": build_prompt(item, tickers)}],
    )
    text = "".join(getattr(b, "text", "") for b in message.content)
    result = parse_response(text)
    if result and result.portfolio_relevance not in ("held", "watchlist", "sector", "none"):
        # Normalize bad enum back to "none".
        result = ImpactScore(
            impact_score=result.impact_score,
            impact_rationale=result.impact_rationale,
            decision_hook=result.decision_hook,
            portfolio_relevance="none",
        )
    return result
```

- [ ] **Step 4: Write pipeline tests**

Create `step2-news/tests/test_pipeline.py`:

```python
from __future__ import annotations

from axe_news.ingest import RawItem
from axe_news.pipeline import assemble_report, classify_relevance
from axe_news.scorer import ImpactScore


def _item(url, title="t", summary=""):
    return RawItem(title=title, url=url, source="reuters-biz", published_at="2026-04-15T00:00:00Z", summary=summary)


def test_classify_relevance_held_beats_watchlist():
    held = {"MSFT"}
    watchlist = {"MSFT", "ORCL"}
    assert classify_relevance(["MSFT", "ORCL"], held, watchlist) == "held"


def test_classify_relevance_watchlist_when_only_watchlist_tickers():
    held = {"MSFT"}
    watchlist = {"MSFT", "ORCL"}
    assert classify_relevance(["ORCL"], held, watchlist) == "watchlist"


def test_classify_relevance_none_when_no_tickers():
    assert classify_relevance([], {"MSFT"}, {"MSFT"}) == "none"


def test_assemble_report_filters_below_6_and_matches_schema():
    scored = [
        (_item("https://a", "strong"), ["MSFT"], "held", ImpactScore(8, "big", "trim", "held")),
        (_item("https://b", "weak"), ["AAPL"], "held", ImpactScore(4, "meh", None, "held")),
        (_item("https://c", "mid"), ["GOOG"], "watchlist", ImpactScore(6, "ok", None, "watchlist")),
    ]
    report = assemble_report(
        scored,
        sources_polled=["reuters-biz"],
        items_in=42,
        generated_at="2026-04-15T09:00:00Z",
    )
    assert report["items_in"] == 42
    assert report["items_kept"] == 2
    assert {it["impact_score"] for it in report["items"]} == {8, 6}
    # Sorted by score descending
    assert report["items"][0]["impact_score"] == 8
    assert report["items"][0]["scored_by"] == "claude-haiku-4-5"
    # Validates against schema
    from axe_core.schemas import NewsReport
    NewsReport.model_validate(report)
```

- [ ] **Step 5: Implement `pipeline.py`**

Create `step2-news/axe_news/pipeline.py`:

```python
"""Pure assembly logic for the news report — no IO."""
from __future__ import annotations

from typing import Iterable, Literal

from axe_news.ingest import RawItem, item_id
from axe_news.scorer import MODEL_NAME_FOR_ARTIFACT, ImpactScore

ScoredTuple = tuple[RawItem, list[str], str, ImpactScore]
PortfolioRelevance = Literal["held", "watchlist", "sector", "none"]


def classify_relevance(
    tickers: list[str],
    held: set[str],
    watchlist: set[str],
) -> PortfolioRelevance:
    if any(t in held for t in tickers):
        return "held"
    if any(t in watchlist for t in tickers):
        return "watchlist"
    if tickers:
        return "sector"
    return "none"


def assemble_report(
    scored: Iterable[ScoredTuple],
    sources_polled: list[str],
    items_in: int,
    generated_at: str,
) -> dict:
    kept = []
    for item, tickers, relevance, score in scored:
        if score.impact_score < 6:
            continue
        kept.append(
            {
                "id": item_id(item),
                "title": item.title,
                "url": item.url,
                "source": item.source,
                "published_at": item.published_at,
                "tickers_mentioned": tickers,
                "portfolio_relevance": relevance,
                "impact_score": score.impact_score,
                "impact_rationale": score.impact_rationale,
                "decision_hook": score.decision_hook,
                "scored_by": MODEL_NAME_FOR_ARTIFACT,
            }
        )
    kept.sort(key=lambda it: it["impact_score"], reverse=True)
    return {
        "generated_at": generated_at,
        "sources_polled": sources_polled,
        "items_in": items_in,
        "items_kept": len(kept),
        "items": kept,
    }
```

- [ ] **Step 6: Implement CLI**

Create `step2-news/axe_news/cli.py`:

```python
"""`axe-news` CLI: fetch, score, write news-latest.json, emit trace."""
from __future__ import annotations

import asyncio
import json
import os

from axe_core import Tracer
from axe_core.paths import public_dir
from axe_news.feeds import FEEDS, yahoo_ticker_feed
from axe_news.ingest import dedupe, extract_tickers, fetch_feed
from axe_news.pipeline import assemble_report, classify_relevance
from axe_news.scorer import score_item
from axe_news.watchlist import load_watchlist


def _atomic_write_json(path, data) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


async def _fetch_all(feeds) -> tuple[list, list[str]]:
    results = await asyncio.gather(*[fetch_feed(f) for f in feeds], return_exceptions=True)
    items = []
    polled: list[str] = []
    for feed, res in zip(feeds, results):
        polled.append(feed.id)
        if isinstance(res, Exception):
            continue
        items.extend(res)
    return items, polled


def main() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY not set")

    watchlist = load_watchlist()
    held = watchlist  # Held subset — same as watchlist for now; refine when holdings drift from profile.

    tracer = Tracer(agent="axe_news")
    tracer.start()
    tracer.event(step="load_watchlist", thought=f"watchlist has {len(watchlist)} tickers")

    feeds = list(FEEDS) + [yahoo_ticker_feed(t) for t in sorted(watchlist)]
    tracer.event(step="fetch_feeds", thought=f"polling {len(feeds)} feeds", io={"in": {"feed_count": len(feeds)}})

    try:
        raw, polled = asyncio.run(_fetch_all(feeds))
    except Exception as exc:
        tracer.event(step="error", thought=f"fetch failed: {exc}")
        tracer.finalize(status="failed", summary=f"fetch failed: {exc}", artifact_written=None)
        raise

    deduped = dedupe(raw)
    tracer.event(
        step="dedupe",
        thought=f"{len(raw)} raw → {len(deduped)} unique",
        io={"in": {"n": len(raw)}, "out": {"n": len(deduped)}},
    )

    scored = []
    scored_count = 0
    for item in deduped:
        tickers = extract_tickers(item, watchlist)
        relevance = classify_relevance(tickers, held, watchlist)
        if relevance == "none":
            continue  # Skip LLM call when nothing in watchlist mentioned.
        try:
            result = score_item(item, tickers, relevance, api_key=api_key)
        except Exception as exc:
            tracer.event(step="score_error", thought=f"skipping item due to {exc}", io={"in": {"url": item.url}})
            continue
        scored_count += 1
        if result is None:
            continue
        scored.append((item, tickers, relevance, result))

    tracer.event(
        step="score",
        thought=f"scored {scored_count} items via Haiku 4.5",
        io={"out": {"scored": scored_count}},
    )

    from datetime import datetime, timezone
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = assemble_report(scored, sources_polled=polled, items_in=len(raw), generated_at=generated_at)

    out_path = public_dir() / "news-latest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(out_path, report)

    tracer.event(
        step="write_artifact",
        thought=f"wrote {report['items_kept']} items to news-latest.json",
    )
    tracer.finalize(
        status="success",
        summary=f"{len(raw)} in, {report['items_kept']} kept (score>=6)",
        artifact_written="news-latest.json",
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: CLI integration test**

Create `step2-news/tests/test_cli.py`:

```python
from __future__ import annotations

import json

from axe_news import cli as news_cli
from axe_news.ingest import RawItem
from axe_news.scorer import ImpactScore
from axe_core import trace as trace_mod


def test_cli_writes_news_latest_and_trace(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)
    monkeypatch.setattr(news_cli, "public_dir", lambda: tmp_path)

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setattr(news_cli, "load_watchlist", lambda: {"MSFT"})

    items = [
        RawItem(title="MSFT probe", url="https://a", source="reuters-biz", published_at="2026-04-15T00:00:00Z", summary="DOJ opens inquiry into MSFT"),
        RawItem(title="weather update", url="https://b", source="reuters-biz", published_at="2026-04-15T00:00:00Z", summary="nothing relevant"),
    ]

    async def fake_fetch_all(feeds):
        return items, [f.id for f in feeds]

    monkeypatch.setattr(news_cli, "_fetch_all", fake_fetch_all)

    def fake_score(item, tickers, relevance, api_key):
        return ImpactScore(8, "big", "consider trim", "held")

    monkeypatch.setattr(news_cli, "score_item", fake_score)

    news_cli.main()

    report = json.loads((tmp_path / "news-latest.json").read_text())
    assert report["items_kept"] == 1
    assert report["items"][0]["title"] == "MSFT probe"

    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert index["runs"][0]["agent"] == "axe_news"
    assert index["runs"][0]["artifact_written"] == "news-latest.json"
    assert index["runs"][0]["status"] == "success"
```

- [ ] **Step 8: Run all new tests**

```bash
cd step2-news && pytest -v
```

Expected: test_ingest (6) + test_scorer (5) + test_pipeline (4) + test_cli (1) = 16 passed.

- [ ] **Step 9: Manual smoke run (requires ANTHROPIC_API_KEY)**

```bash
cd step2-news && ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY axe-news
```

Expected: exits 0, `step6-dashboard/public/news-latest.json` exists and validates:

```bash
python -c "import json; from axe_core.schemas import NewsReport; NewsReport.model_validate(json.loads(open('step6-dashboard/public/news-latest.json').read())); print('ok')"
```

Expected stdout: `ok`.

- [ ] **Step 10: Commit**

```bash
git add step2-news/axe_news/ step2-news/tests/
git commit -m "feat(axe_news): LLM impact scorer, pipeline, CLI → news-latest.json + trace"
```

---

## Task 12: `axe_orchestrator health` — regenerate `health.json` + Panel 1 freshness badge

**Files:**
- Create: `step7-automation/axe_orchestrator/health.py`
- Modify: `step7-automation/axe_orchestrator/cli.py` (add `health` subcommand)
- Modify: `step6-dashboard/src/components/PortfolioPanel.jsx` (freshness badge)
- Create: `step7-automation/tests/test_health.py`

`health.json` (spec §5.6) must be refreshed after every `run` so Panels 1 and 5 reflect the truth. Also implements the freshness badge on Panel 1 per spec §6 row 1.

- [ ] **Step 1: Tests for `health.generate`**

Create `step7-automation/tests/test_health.py`:

```python
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from axe_orchestrator.health import compute_status, generate_health


def test_compute_status_buckets():
    now = datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc)
    fresh = (now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    stale = (now - timedelta(minutes=500)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert compute_status(fresh, 240, now=now)[1] == "fresh"
    assert compute_status(stale, 240, now=now)[1] == "stale"
    assert compute_status(None, 240, now=now) == (None, "missing")


def test_generate_health_reads_artifacts(tmp_path):
    public = tmp_path
    (public / "traces").mkdir()
    (public / "portfolio.json").write_text('{"generated_at":"2026-04-15T09:00:00Z"}')
    (public / "alpha-latest.json").write_text('{"generated_at":"2026-04-15T05:00:00Z"}')
    now = datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc)

    report = generate_health(public_dir=public, now=now)
    assert report["artifacts"]["portfolio"]["status"] == "fresh"
    assert report["artifacts"]["alpha"]["status"] == "fresh"
    assert report["artifacts"]["news"]["status"] == "missing"
    assert report["freshness_thresholds_min"] == {"portfolio": 240, "alpha": 1440, "news": 60}

    from axe_core.schemas import HealthReport
    HealthReport.model_validate(report)
```

- [ ] **Step 2: Run test, confirm failure**

```bash
cd step7-automation && pytest tests/test_health.py -v
```

Expected: FAIL — module missing.

- [ ] **Step 3: Implement `health.py`**

Create `step7-automation/axe_orchestrator/health.py`:

```python
"""Generate health.json from artifact mtimes / generated_at fields."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from axe_core.paths import public_dir

THRESHOLDS_MIN = {"portfolio": 240, "alpha": 1440, "news": 60}
ARTIFACT_FILES = {
    "portfolio": "portfolio.json",
    "alpha": "alpha-latest.json",
    "news": "news-latest.json",
    "traces": "traces/index.json",
}


def _read_generated_at(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return data.get("generated_at")
    except Exception:
        return None


def compute_status(last_refresh: str | None, threshold_min: int, now: datetime) -> tuple[int | None, str]:
    if not last_refresh:
        return (None, "missing")
    try:
        ts = datetime.strptime(last_refresh[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return (None, "missing")
    age_min = int((now - ts).total_seconds() // 60)
    return (age_min, "fresh" if age_min <= threshold_min else "stale")


def generate_health(public_dir: Path, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    artifacts: dict = {}
    for key, rel in ARTIFACT_FILES.items():
        last = _read_generated_at(public_dir / rel)
        threshold = THRESHOLDS_MIN.get(key, 1440)
        age_min, status = compute_status(last, threshold, now=now)
        artifacts[key] = {"last_refresh": last, "age_min": age_min, "status": status}
    return {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifacts": artifacts,
        "freshness_thresholds_min": THRESHOLDS_MIN,
    }


def write_health() -> Path:
    pub = public_dir()
    report = generate_health(pub)
    out = pub / "health.json"
    tmp = out.with_name("health.json.tmp")
    tmp.write_text(json.dumps(report, indent=2))
    tmp.replace(out)
    return out
```

- [ ] **Step 4: Wire `health` into CLI**

Edit `step7-automation/axe_orchestrator/cli.py`. Add `health` subcommand — after the existing `run` subparser setup insert:

```python
    sub.add_parser("health", help="Regenerate health.json from current artifacts")
```

Before the existing `if args.cmd != "run":` guard, add:

```python
    if args.cmd == "health":
        from axe_orchestrator.health import write_health
        path = write_health()
        print(f"[axe] wrote {path}")
        return 0
```

Then after every `run` completes (inside `main`, at the bottom of both the `all` branch and the single-target branch), regenerate health so Panel 5 is always current. Wrap the return:

```python
    from axe_orchestrator.health import write_health
    try:
        write_health()
    except Exception as exc:
        print(f"[axe] warning: failed to write health.json: {exc}")
    return rc  # rc = the previous return value; rename local accordingly
```

- [ ] **Step 5: Run tests**

```bash
cd step7-automation && pytest -v
```

Expected: existing CLI tests still pass + 2 health tests pass.

- [ ] **Step 6: Add freshness badge to `PortfolioPanel`**

Edit `step6-dashboard/src/components/PortfolioPanel.jsx`. Add a `useEffect` alongside the existing `portfolio.json` fetch that also loads `/health.json`, and render a small chip next to the panel title:

```jsx
function FreshnessBadge({ health }) {
  if (!health) return null;
  const portfolio = health.artifacts?.portfolio;
  if (!portfolio) return null;
  const color = {
    fresh: "bg-green-100 text-green-800",
    stale: "bg-yellow-100 text-yellow-800",
    missing: "bg-red-100 text-red-800",
  }[portfolio.status] || "bg-gray-100 text-gray-700";
  const label = portfolio.age_min != null ? `${portfolio.status} · ${portfolio.age_min}m old` : portfolio.status;
  return <span className={`text-xs px-2 py-0.5 rounded ${color}`}>{label}</span>;
}
```

Fetch `/health.json` on mount and pass the result to `<FreshnessBadge health={health} />` next to the panel's heading.

- [ ] **Step 7: Manual verify dev server**

```bash
cd step6-dashboard && npm run dev
```

Confirm Portfolio panel title shows a colored chip `fresh · Nm old` (or `missing` if `health.json` not written yet). Trigger:

```bash
axe health
```

Reload, chip should update.

- [ ] **Step 8: Commit**

```bash
git add step7-automation/axe_orchestrator/health.py step7-automation/axe_orchestrator/cli.py step7-automation/tests/test_health.py step6-dashboard/src/components/PortfolioPanel.jsx
git commit -m "feat(orchestrator+dashboard): health.json generator + Panel 1 freshness badge"
```

---

## Task 13: Panel 4 — Hot News (replaces ResearchPanel)

**Files:**
- Delete: `step6-dashboard/src/components/ResearchPanel.jsx`
- Create: `step6-dashboard/src/components/NewsPanel.jsx`
- Modify: `step6-dashboard/src/App.jsx`

Panel reads `news-latest.json` (Task 11) and renders items ranked by impact score with ticker pills and relevance chips.

- [ ] **Step 1: Create `NewsPanel.jsx`**

Create `step6-dashboard/src/components/NewsPanel.jsx`:

```jsx
import { useEffect, useState } from "react";

function scoreColor(score) {
  if (score >= 9) return "bg-red-600 text-white";
  if (score >= 7) return "bg-orange-500 text-white";
  return "bg-yellow-400 text-black";
}

function relevanceChip(rel) {
  const colors = {
    held: "bg-blue-600 text-white",
    watchlist: "bg-blue-300 text-black",
    sector: "bg-gray-200 text-gray-800",
    none: "bg-gray-100 text-gray-500",
  };
  return colors[rel] || colors.none;
}

function NewsItem({ item }) {
  return (
    <article className="border-b border-gray-100 py-3">
      <div className="flex items-center gap-2 mb-1">
        <span className={`text-xs px-2 py-0.5 rounded ${scoreColor(item.impact_score)}`}>
          impact {item.impact_score}
        </span>
        <span className={`text-xs px-2 py-0.5 rounded ${relevanceChip(item.portfolio_relevance)}`}>
          {item.portfolio_relevance}
        </span>
        {item.tickers_mentioned?.map((t) => (
          <span key={t} className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded">{t}</span>
        ))}
        <span className="ml-auto text-xs text-gray-500">{item.source} · {item.published_at}</span>
      </div>
      <a href={item.url} target="_blank" rel="noreferrer" className="font-semibold text-gray-900 hover:underline">
        {item.title}
      </a>
      <p className="text-sm text-gray-700 mt-1">{item.impact_rationale}</p>
      {item.decision_hook && (
        <p className="text-sm text-blue-700 mt-1">→ {item.decision_hook}</p>
      )}
    </article>
  );
}

export default function NewsPanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/news-latest.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Hot News</h2><p className="text-red-600">Failed to load: {error}</p></section>;
  if (!data) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Hot News</h2><p className="text-gray-500">Loading…</p></section>;

  return (
    <section className="p-4">
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-xl font-bold">Hot News</h2>
        <span className="text-xs text-gray-500">{data.items_kept} kept of {data.items_in} · {data.generated_at}</span>
      </div>
      {data.items.length === 0 ? (
        <p className="text-gray-500 text-sm">No items cleared the impact threshold.</p>
      ) : (
        data.items.map((it) => <NewsItem key={it.id} item={it} />)
      )}
    </section>
  );
}
```

- [ ] **Step 2: Swap in `App.jsx`**

In `step6-dashboard/src/App.jsx`:

1. Remove `import ResearchPanel from "./components/ResearchPanel.jsx";`
2. Add `import NewsPanel from "./components/NewsPanel.jsx";`
3. Replace `<ResearchPanel ... />` with `<NewsPanel />`.

- [ ] **Step 3: Delete `ResearchPanel.jsx`**

```bash
git rm step6-dashboard/src/components/ResearchPanel.jsx
```

- [ ] **Step 4: Manual verify**

```bash
cd step6-dashboard && npm run dev
```

Confirm: panel titled "Hot News" with `N kept of M` counter, items sorted by impact score descending, ticker pills, relevance chip, clicking title opens source URL in new tab, `decision_hook` arrow line shows when present, 404 case renders red "Failed to load".

- [ ] **Step 5: Lint + commit**

```bash
cd step6-dashboard && npm run lint
git add step6-dashboard/src/components/NewsPanel.jsx step6-dashboard/src/App.jsx
git commit -m "feat(dashboard): replace Research panel with Hot News from news-latest.json"
```

---

## Task 14: Panel 5 — Agent Status Board (rebuild from `health.json` + `traces/index.json`)

**Files:**
- Modify: `step6-dashboard/src/components/AutomationPanel.jsx` → rename to `AgentStatusPanel.jsx`
- Modify: `step6-dashboard/src/App.jsx`

Spec §6 row 5: rebuild the Automation panel to show each agent's latest run with status, timing, and a link into the trace viewer (Task 15).

- [ ] **Step 1: Rename component**

```bash
git mv step6-dashboard/src/components/AutomationPanel.jsx step6-dashboard/src/components/AgentStatusPanel.jsx
```

- [ ] **Step 2: Replace contents of `AgentStatusPanel.jsx`**

```jsx
import { useEffect, useState } from "react";

const AGENTS = ["axe_portfolio", "axe_alpha", "axe_news"];

function statusDot(status) {
  return {
    success: "bg-green-500",
    partial: "bg-yellow-500",
    failed: "bg-red-500",
    missing: "bg-gray-300",
  }[status] || "bg-gray-300";
}

function AgentRow({ agent, latest, health, onOpenTrace }) {
  const status = latest?.status || "missing";
  const duration = latest ? `${Math.round(latest.duration_ms / 1000)}s` : "—";
  const freshness = health?.artifacts?.[agentKey(agent)]?.status || "missing";
  const freshnessColor = {
    fresh: "text-green-700",
    stale: "text-yellow-700",
    missing: "text-red-700",
  }[freshness];
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-100">
      <span className={`w-2 h-2 rounded-full ${statusDot(status)}`} />
      <span className="font-mono w-36 shrink-0">{agent}</span>
      <span className="text-xs text-gray-500 w-24">{status}</span>
      <span className="text-xs text-gray-500 w-16">{duration}</span>
      <span className={`text-xs ${freshnessColor} w-28`}>{freshness}</span>
      <span className="text-xs text-gray-600 truncate flex-1">{latest?.summary || "no runs yet"}</span>
      {latest && (
        <button
          onClick={() => onOpenTrace(latest.run_id)}
          className="text-xs text-blue-600 hover:underline"
        >
          view trace →
        </button>
      )}
    </div>
  );
}

function agentKey(agent) {
  // Map agent names to health.json artifact keys.
  return { axe_portfolio: "portfolio", axe_alpha: "alpha", axe_news: "news" }[agent] || agent;
}

export default function AgentStatusPanel({ onOpenTrace = () => {} }) {
  const [index, setIndex] = useState(null);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/traces/index.json").then((r) => (r.ok ? r.json() : { runs: [] })),
      fetch("/health.json").then((r) => (r.ok ? r.json() : null)),
    ])
      .then(([idx, h]) => { setIndex(idx); setHealth(h); })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Agent Status</h2><p className="text-red-600">Failed to load: {error}</p></section>;
  if (!index) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Agent Status</h2><p className="text-gray-500">Loading…</p></section>;

  const latestByAgent = {};
  for (const run of index.runs) {
    if (!latestByAgent[run.agent]) latestByAgent[run.agent] = run;
  }

  return (
    <section className="p-4">
      <h2 className="text-xl font-bold mb-3">Agent Status</h2>
      {AGENTS.map((agent) => (
        <AgentRow
          key={agent}
          agent={agent}
          latest={latestByAgent[agent]}
          health={health}
          onOpenTrace={onOpenTrace}
        />
      ))}
      <div className="mt-4 text-xs text-gray-500">
        {index.runs.length} runs in index · {Object.keys(latestByAgent).length} agents tracked
      </div>
    </section>
  );
}
```

- [ ] **Step 3: Update `App.jsx`**

Change `import AutomationPanel from …AutomationPanel.jsx;` → `import AgentStatusPanel from "./components/AgentStatusPanel.jsx";`. Replace JSX usage, wire the `onOpenTrace` callback to App-level state that will be consumed by the trace viewer in Task 15 (for now pass a no-op).

- [ ] **Step 4: Manual verify**

Start dev server. Confirm: one row per agent, colored dot, duration, freshness cell, "view trace →" link present when run exists, "no runs yet" fallback otherwise.

- [ ] **Step 5: Lint + commit**

```bash
cd step6-dashboard && npm run lint
git add step6-dashboard/src/components/AgentStatusPanel.jsx step6-dashboard/src/App.jsx
git commit -m "feat(dashboard): rebuild Automation as Agent Status Board"
```

---

## Task 15: Panel 6 — Internal Dialogue Viewer (trace playback)

**Files:**
- Create: `step6-dashboard/src/components/TraceViewerPanel.jsx`
- Modify: `step6-dashboard/src/App.jsx` (wire trace state; connect Agent Status Board's "view trace →" button)

Panel 6 is NEW per spec §6 row 6. Given a `run_id`, fetch `traces/<run_id>.json` and play back events step-by-step.

- [ ] **Step 1: Create `TraceViewerPanel.jsx`**

```jsx
import { useEffect, useRef, useState } from "react";

function Event({ ev }) {
  return (
    <div className="border-l-2 border-blue-300 pl-3 py-2">
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <span className="font-mono">#{ev.seq}</span>
        <span>{ev.t}</span>
        <span className="font-semibold text-gray-800">{ev.step}</span>
        {ev.elapsed_ms != null && <span>{ev.elapsed_ms}ms</span>}
      </div>
      {ev.thought && <p className="text-sm text-gray-900 mt-1">{ev.thought}</p>}
      {ev.io && (
        <pre className="text-xs bg-gray-50 p-2 rounded mt-1 overflow-auto">
          {JSON.stringify(ev.io, null, 2)}
        </pre>
      )}
      {ev.rejected && (
        <div className="text-xs text-red-700 mt-1">rejected: {ev.rejected.join(", ")}</div>
      )}
    </div>
  );
}

export default function TraceViewerPanel({ runId }) {
  const [trace, setTrace] = useState(null);
  const [error, setError] = useState(null);
  const [playIdx, setPlayIdx] = useState(null);
  const timer = useRef(null);

  useEffect(() => {
    setTrace(null);
    setError(null);
    setPlayIdx(null);
    if (!runId) return;
    fetch(`/traces/${runId}.json`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((data) => {
        setTrace(data);
        setPlayIdx(data.events.length); // fully revealed by default
      })
      .catch((e) => setError(e.message));
  }, [runId]);

  function play() {
    if (!trace) return;
    setPlayIdx(0);
    clearInterval(timer.current);
    timer.current = setInterval(() => {
      setPlayIdx((i) => {
        if (i >= trace.events.length) {
          clearInterval(timer.current);
          return i;
        }
        return i + 1;
      });
    }, 500);
  }

  useEffect(() => () => clearInterval(timer.current), []);

  if (!runId) {
    return (
      <section className="p-4">
        <h2 className="text-xl font-bold mb-2">Agent Dialogue</h2>
        <p className="text-gray-500 text-sm">Pick a run from the Agent Status Board.</p>
      </section>
    );
  }
  if (error) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Agent Dialogue</h2><p className="text-red-600">Failed to load: {error}</p></section>;
  if (!trace) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Agent Dialogue</h2><p className="text-gray-500">Loading…</p></section>;

  const shown = trace.events.slice(0, playIdx);

  return (
    <section className="p-4">
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-xl font-bold">Agent Dialogue — {trace.agent}</h2>
        <button onClick={play} className="text-xs px-2 py-1 rounded bg-blue-600 text-white">▶ replay</button>
      </div>
      <div className="text-xs text-gray-500 mb-2">
        run {trace.run_id} · {trace.status} · {trace.started_at} → {trace.ended_at}
      </div>
      <p className="text-sm text-gray-800 mb-3">{trace.summary}</p>
      <div className="space-y-1">
        {shown.map((ev) => <Event key={ev.seq} ev={ev} />)}
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Wire state in `App.jsx`**

Inside `App`:

```jsx
const [activeRunId, setActiveRunId] = useState(null);
// ...
<AgentStatusPanel onOpenTrace={setActiveRunId} />
<TraceViewerPanel runId={activeRunId} />
```

Import `useState` and the new component.

- [ ] **Step 3: Manual verify**

Start dev server. Seed a trace by running an agent (e.g. `axe run portfolio`). In the dashboard click "view trace →" on the Portfolio row; confirm the dialogue panel fills with events, "▶ replay" reveals them progressively at 500ms cadence. Pick a different run: viewer swaps cleanly.

- [ ] **Step 4: Lint + commit**

```bash
cd step6-dashboard && npm run lint
git add step6-dashboard/src/components/TraceViewerPanel.jsx step6-dashboard/src/App.jsx
git commit -m "feat(dashboard): Agent Dialogue viewer with event-by-event replay"
```

---

## Task 16: FastAPI backend — `/health`, `/refresh/{agent}`, SSE `/trace/stream/{run_id}`

**Files:**
- Create: `step7-automation/axe_orchestrator/api.py`
- Create: `step7-automation/tests/test_api.py`

Thin FastAPI. `/refresh` shells out the same runners used by the CLI. SSE streams the latest trace events as they're appended; since our current Tracer writes trace files only on `finalize()`, the SSE implementation polls the trace file on an interval and emits new events. Good enough for the B-milestone; a pub/sub upgrade is endgame work.

- [ ] **Step 1: Write API tests**

Create `step7-automation/tests/test_api.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from axe_orchestrator import api as api_mod
from axe_orchestrator.api import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir()
    (tmp_path / "health.json").write_text(json.dumps({
        "generated_at": "2026-04-15T10:00:00Z",
        "artifacts": {"portfolio": {"last_refresh": "2026-04-15T09:00:00Z", "age_min": 60, "status": "fresh"}},
        "freshness_thresholds_min": {"portfolio": 240, "alpha": 1440, "news": 60},
    }))
    monkeypatch.setattr(api_mod, "public_dir", lambda: tmp_path)
    return TestClient(app)


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["artifacts"]["portfolio"]["status"] == "fresh"


def test_refresh_agent_invokes_runner(client, monkeypatch):
    called = []
    monkeypatch.setattr(api_mod.runners, "run_alpha", lambda: called.append("alpha") or 0)
    r = client.post("/refresh/alpha")
    assert r.status_code == 200
    assert called == ["alpha"]
    assert r.json()["rc"] == 0


def test_refresh_unknown_agent_404(client):
    r = client.post("/refresh/bogus")
    assert r.status_code == 404
```

- [ ] **Step 2: Run tests — expect FAIL (missing api module)**

```bash
cd step7-automation && pip install -e .[test,api] && pytest tests/test_api.py -v
```

Expected: FAIL on import.

- [ ] **Step 3: Implement `api.py`**

Create `step7-automation/axe_orchestrator/api.py`:

```python
"""Thin FastAPI wrapper around axe_orchestrator runners + SSE trace streaming."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from axe_core.paths import public_dir
from axe_orchestrator import runners

app = FastAPI(title="Axe Orchestrator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

AGENT_RUNNERS = {
    "alpha": runners.run_alpha,
    "news": runners.run_news,
    "portfolio": runners.run_portfolio,
}


@app.get("/health")
def get_health():
    path = public_dir() / "health.json"
    if not path.exists():
        raise HTTPException(404, "health.json missing")
    return json.loads(path.read_text())


@app.post("/refresh/{agent}")
def refresh(agent: str):
    runner = AGENT_RUNNERS.get(agent)
    if runner is None:
        raise HTTPException(404, f"unknown agent: {agent}")
    rc = runner()
    return {"agent": agent, "rc": rc}


@app.get("/trace/stream/{run_id}")
async def stream_trace(run_id: str):
    path = public_dir() / "traces" / f"{run_id}.json"

    async def events():
        last_seq = 0
        while True:
            if path.exists():
                try:
                    data = json.loads(path.read_text())
                except json.JSONDecodeError:
                    data = None
                if data:
                    for ev in data.get("events", []):
                        if ev["seq"] > last_seq:
                            last_seq = ev["seq"]
                            yield {"event": "trace", "data": json.dumps(ev)}
                    if data.get("status") in ("success", "failed", "partial"):
                        yield {"event": "done", "data": json.dumps({"status": data["status"], "summary": data.get("summary")})}
                        return
            await asyncio.sleep(1.0)

    return EventSourceResponse(events())
```

- [ ] **Step 4: Run tests**

```bash
cd step7-automation && pytest tests/test_api.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Manual smoke**

```bash
cd step7-automation && uvicorn axe_orchestrator.api:app --reload --port 8787 &
curl -s http://localhost:8787/health | head -c 200
curl -s -X POST http://localhost:8787/refresh/portfolio
kill %1
```

Expected: health JSON prints, refresh returns `{"agent":"portfolio","rc":0}` (or non-zero with an agent error), trace file appears under `public/traces/`.

- [ ] **Step 6: Commit**

```bash
git add step7-automation/axe_orchestrator/api.py step7-automation/tests/test_api.py step7-automation/pyproject.toml
git commit -m "feat(orchestrator): FastAPI backend — /health, /refresh, SSE /trace/stream"
```

---

## Task 17: Dashboard — use API when available, fall back to files

**Files:**
- Create: `step6-dashboard/src/lib/api.js`
- Modify: `step6-dashboard/src/components/PortfolioPanel.jsx` (consume `loadHealth`)
- Modify: `step6-dashboard/src/components/AgentStatusPanel.jsx` (Refresh buttons + SSE hook)
- Modify: `step6-dashboard/src/components/TraceViewerPanel.jsx` (use SSE when API up)
- Create: `step6-dashboard/.env.development` (`VITE_API_BASE=http://localhost:8787`)

Principle from spec §3: "Dashboard is always readable from files alone. Backend is additive — panels must gracefully degrade if the API is down."

- [ ] **Step 1: Create API shim**

Create `step6-dashboard/src/lib/api.js`:

```js
const API = import.meta.env.VITE_API_BASE || "";

async function tryApi(path) {
  if (!API) return null;
  try {
    const r = await fetch(`${API}${path}`);
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
}

export async function loadHealth() {
  const api = await tryApi("/health");
  if (api) return api;
  const r = await fetch("/health.json");
  return r.ok ? r.json() : null;
}

export async function refreshAgent(agent) {
  if (!API) throw new Error("API not configured");
  const r = await fetch(`${API}/refresh/${agent}`, { method: "POST" });
  if (!r.ok) throw new Error(`refresh failed: ${r.status}`);
  return r.json();
}

export function streamTrace(runId, onEvent, onDone) {
  if (!API) return null;
  const src = new EventSource(`${API}/trace/stream/${runId}`);
  src.addEventListener("trace", (e) => onEvent(JSON.parse(e.data)));
  src.addEventListener("done", (e) => { onDone(JSON.parse(e.data)); src.close(); });
  src.onerror = () => src.close();
  return src;
}
```

Create `step6-dashboard/.env.development`:

```
VITE_API_BASE=http://localhost:8787
```

- [ ] **Step 2: Use `loadHealth` in `PortfolioPanel`**

Replace the hand-rolled `/health.json` fetch with `loadHealth()` from `../lib/api.js`. No behavior change when API is down — still shows a badge from the file.

- [ ] **Step 3: Add Refresh button + live SSE to AgentStatusPanel**

In `AgentStatusPanel.jsx`, import `refreshAgent` from `../lib/api.js`. Add a small `Refresh` button on each agent row that calls `refreshAgent(agentKey(agent))` and on resolution re-fetches `/traces/index.json`. Disable the button during the in-flight call; if `refreshAgent` throws, show a short inline error next to the row.

- [ ] **Step 4: Use `streamTrace` in TraceViewerPanel**

In `TraceViewerPanel.jsx`, after the initial fetch loads the committed file, if `streamTrace` is available, subscribe to new events and append them to `trace.events` as they arrive. When the `done` event fires, update `trace.status`. On unmount, close the EventSource.

- [ ] **Step 5: Manual verify both paths**

- With FastAPI running at :8787: refresh button triggers a new run, Panel 5 updates, Panel 6 live-streams events while the run is in-flight.
- Kill the FastAPI process. Reload. Dashboard still renders from files. Refresh button shows its error state cleanly without crashing the page.

- [ ] **Step 6: Lint + commit**

```bash
cd step6-dashboard && npm run lint
git add step6-dashboard/src/lib/api.js step6-dashboard/.env.development step6-dashboard/src/components/
git commit -m "feat(dashboard): API integration with file fallback + SSE trace live view"
```

---

## Task 18: Cron + Telegram integration docs + B-milestone verification

**Files:**
- Create: `runbooks/cron-integration.md`
- Create: `runbooks/telegram-integration.md`
- Modify: `spec/15-04-2026-research-platform-design.md` (mark §9 DoD checkboxes)

Last task of the milestone: document the endgame wiring paths so the handoff is additive (no code this week). Then execute the DoD checklist in spec §9.

- [ ] **Step 1: Write `runbooks/cron-integration.md`**

Create `runbooks/cron-integration.md` documenting:

1. The single entrypoint: `axe run all` from `step7-automation/`.
2. Example crontab entry:
   ```
   0 6 * * 1-5 cd /home/tiger/.openclaw/workspace/projects/Axe-Capital && /usr/bin/env -S bash -lc 'axe run all' >> /var/log/axe.log 2>&1
   ```
3. How `axe health` is run after `run all` (already inside CLI in Task 12) — no second cron entry.
4. Rotation: the 500-run global cap (Task 2) means log size is bounded; no external janitor.
5. Failure behavior: exit code = failure count. Cron sends mail on non-zero exit if `MAILTO` is set.

- [ ] **Step 2: Write `runbooks/telegram-integration.md`**

Document the integration contract so the endgame is additive:

1. New file to create later: `step7-automation/axe_orchestrator/alerts.py` exposing `send(message: str) -> None` reading `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` from env.
2. Hook point: after each `Tracer.finalize`, emit an alert when (a) `status == "failed"`, or (b) `axe_news` kept any `impact_score >= 8` item, or (c) `axe_alpha` surfaced a `conviction_score >= 8` opportunity.
3. Rate limiting: at most one alert per agent per 6h for the same run_id seed — stored in `public/.alerts-state.json` (not versioned).
4. Degradation: if the env vars are missing, `alerts.send()` is a no-op. Tracer never fails because of Telegram.

- [ ] **Step 3: Execute the DoD checklist**

Run from `projects/Axe-Capital/`:

```bash
axe run all && axe health
```

Expected: exit 0. Then verify each spec §9 item:

1. **All 7 panels populated with real, current data** — open dashboard, confirm Portfolio, Targets, Alpha, News, AgentStatus, TraceViewer, DecisionArchive all render without errors and show fresh data.
2. **User can trigger a refresh from the dashboard** — click "Refresh" on an agent row, confirm the run kicks off and Panel 5 updates.
3. **User can watch an agent think in real time** — start a refresh, open Panel 6 with the new run_id, confirm events stream in live via SSE.
4. **User can browse past decisions and jump to the producing trace** — open Decision Archive, pick an entry with a `run_id` reference (if present in your data), confirm the UI hands the id to the trace viewer. If no entries carry `run_id` yet, note this as a follow-up — beyond B-milestone scope.
5. **`axe run all` exits 0 on a clean box with only fresh IBKR CSV + internet** — re-run once in a fresh shell to confirm no stale state assumptions.

- [ ] **Step 4: Mark spec §9 checkboxes**

Edit `spec/15-04-2026-research-platform-design.md` §9 (Definition of Done). Convert the five bullets to checkboxes and mark each based on the outcome of Step 3. For any unchecked item, append a one-line follow-up note.

- [ ] **Step 5: Tag the release**

```bash
git add runbooks/cron-integration.md runbooks/telegram-integration.md spec/15-04-2026-research-platform-design.md
git commit -m "docs: cron + Telegram integration paths, B-milestone DoD verification"
git tag -a v0.B -m "Research platform B-milestone complete"
```

Expected: tag created. Do NOT push the tag — the user will push when ready.

---

# Self-Review Notes

**Spec coverage audit:**

| Spec section | Covered by |
|---|---|
| §4 module layout | Tasks 1–6, 10–11, 16 |
| §5.1 alpha-latest.json | Task 4 (writer) + Task 8 (reader) |
| §5.2 news-latest.json | Tasks 10–11 (writer) + Task 13 (reader) |
| §5.3 traces/<run-id>.json | Task 2 (writer) + Task 15 (reader) |
| §5.4 traces/index.json | Task 2 (writer+pruning) + Task 14 (reader) |
| §5.5 decision-log.jsonl extensions | Task 9 (reader tolerates missing fields) |
| §5.6 health.json | Task 12 (writer) + Panels 1 & 5 (readers) |
| §6 Panels 1–7 | Panel 1 freshness: Task 12. Panel 2: Task 7. Panel 3: Task 8. Panel 4: Task 13. Panel 5: Task 14. Panel 6: Task 15. Panel 7: Task 9 |
| §7 testing | pytest in every Python task; manual dev-server verify in every panel task |
| §8 Week 1 | Tasks 1–7 |
| §8 Week 2 | Tasks 8–11 |
| §8 Week 3 | Tasks 12–15 |
| §8 Week 4 | Tasks 16–18 |
| §9 DoD | Task 18 Step 3 |

**Known trade-offs flagged during write-up:**

1. SSE in Task 16 polls the committed trace file on a 1s tick rather than streaming in-process events — chosen because the current Tracer writes only in `finalize()`. A pub/sub upgrade is explicitly endgame.
2. Held/watchlist are currently the same set (Task 11 Step 6). Splitting "held" from "watchlist" requires reading a live position list — deferred until the portfolio panel exposes that as a shared artifact.
3. Task 9's Decision Archive references a future "jump to trace" link (Task 18 DoD item 4). Legacy decision-log entries may lack `run_id`; the DoD step flags this as a follow-up rather than blocking the milestone.
4. `run_news` in `axe_orchestrator/runners.py` points to `step2-news/` per spec §4 (NOT `step3-news/`). Confirmed against spec lines 71 and 75.

**Placeholder scan:** none found — every code-producing step ships literal code.

**Type consistency audit:** `run_id`, `agent`, `started_at`, `ended_at`, `duration_ms`, `status`, `event_count`, `summary`, `artifact_written` are spelled the same in `axe_core.trace`, `axe_core.schemas.TraceIndexRun`, and every panel consumer. `impact_score`, `impact_rationale`, `decision_hook`, `portfolio_relevance`, `tickers_mentioned`, `scored_by` consistent across scorer, pipeline, schema, and `NewsPanel`.

---

# Execution Handoff

Plan complete and saved to `projects/Axe-Capital/plans/15-04-2026-research-platform-plan.md`. Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
