"""Agent trace library — one trace file per run, atomic index updates, pruning."""
from __future__ import annotations

import json
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
    "axe_decision": "decision",
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
        self._write_trace(status="partial", summary="run started")

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
        self._write_trace(status="partial", summary=f"{self.agent} running")

    def finalize(
        self,
        status: Status,
        summary: str,
        artifact_written: str | None = None,
    ) -> None:
        ended = self.now()
        ended_str = ended.strftime("%Y-%m-%dT%H:%M:%SZ")
        duration_ms = self._duration_ms(ended)

        trace_dir = self._trace_dir()
        self._write_trace(status=status, summary=summary, ended_at=ended_str)

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

    def _trace_dir(self) -> Path:
        trace_dir = _public_dir() / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        return trace_dir

    def _write_trace(
        self,
        *,
        status: Status,
        summary: str,
        ended_at: str | None = None,
    ) -> None:
        payload = {
            "run_id": self.run_id,
            "agent": self.agent,
            "started_at": self.started_at,
            "status": status,
            "summary": summary,
            "events": self._events,
        }
        if ended_at is not None:
            payload["ended_at"] = ended_at
        _atomic_write_json(self._trace_dir() / f"{self.run_id}.json", payload)


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
