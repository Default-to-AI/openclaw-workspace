"""Thin FastAPI backend for health, refresh, and live trace streaming."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from axe_core.paths import public_dir
from axe_orchestrator import runners
from axe_orchestrator.health import generate_health, write_health

AGENT_RUNNERS: dict[str, Callable[[], int]] = {
    "portfolio": runners.run_portfolio,
    "alpha": runners.run_alpha,
    "news": runners.run_news,
}
REFRESH_LOCK = asyncio.Lock()


def _trace_path(run_id: str) -> Path:
    return public_dir() / "traces" / f"{run_id}.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


async def _run_agent(target: str) -> dict:
    loop = asyncio.get_running_loop()

    if target == "all":
        results: dict[str, int] = {}
        for name in runners.AGENT_ORDER:
            results[name] = await loop.run_in_executor(None, AGENT_RUNNERS[name])
        write_health()
        return {
            "target": target,
            "ok": all(code == 0 for code in results.values()),
            "results": results,
            "failure_count": sum(1 for code in results.values() if code != 0),
        }

    if target not in AGENT_RUNNERS:
        raise HTTPException(status_code=404, detail=f"Unknown target: {target}")

    rc = await loop.run_in_executor(None, AGENT_RUNNERS[target])
    write_health()
    return {
        "target": target,
        "ok": rc == 0,
        "return_code": rc,
        "failure_count": 0 if rc == 0 else 1,
    }


def create_app() -> FastAPI:
    app = FastAPI(title="Axe Capital API", version="0.1.0")

    @app.get("/health")
    async def health() -> JSONResponse:
        pub = public_dir()
        health_path = pub / "health.json"
        if not health_path.exists():
            write_health()
        report = generate_health(pub)
        return JSONResponse(report)

    @app.post("/refresh/{target}")
    async def refresh(target: str) -> JSONResponse:
        if REFRESH_LOCK.locked():
            raise HTTPException(status_code=409, detail="A refresh is already in progress")
        async with REFRESH_LOCK:
            payload = await _run_agent(target)
        return JSONResponse(payload)

    @app.get("/trace/stream/{run_id}")
    async def trace_stream(run_id: str, request: Request) -> EventSourceResponse:
        trace_path = _trace_path(run_id)

        async def event_generator():
            sent_waiting = False
            last_seq = 0
            sent_meta = False

            while True:
                if await request.is_disconnected():
                    break

                if not trace_path.exists():
                    if not sent_waiting:
                        sent_waiting = True
                        yield {
                            "event": "waiting",
                            "data": json.dumps({"run_id": run_id, "status": "waiting"}),
                        }
                    await asyncio.sleep(1)
                    continue

                trace = _load_json(trace_path)
                if not sent_meta:
                    sent_meta = True
                    yield {
                        "event": "meta",
                        "data": json.dumps(
                            {
                                "run_id": trace.get("run_id"),
                                "agent": trace.get("agent"),
                                "started_at": trace.get("started_at"),
                                "ended_at": trace.get("ended_at"),
                                "status": trace.get("status"),
                                "summary": trace.get("summary"),
                            }
                        ),
                    }

                events = trace.get("events", [])
                new_events = [ev for ev in events if ev.get("seq", 0) > last_seq]
                for ev in new_events:
                    last_seq = max(last_seq, ev.get("seq", 0))
                    yield {
                        "event": "event",
                        "id": str(ev.get("seq", "")),
                        "data": json.dumps(ev),
                    }

                if trace.get("status") in {"success", "failed"}:
                    yield {
                        "event": "done",
                        "data": json.dumps(
                            {
                                "run_id": trace.get("run_id"),
                                "status": trace.get("status"),
                                "summary": trace.get("summary"),
                                "ended_at": trace.get("ended_at"),
                                "event_count": len(events),
                            }
                        ),
                    }
                    break

                await asyncio.sleep(1)

        return EventSourceResponse(event_generator(), ping=10)

    return app


app = create_app()
