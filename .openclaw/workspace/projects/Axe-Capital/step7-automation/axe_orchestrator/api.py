"""Thin FastAPI backend for health, refresh, and live trace streaming."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Callable
from uuid import uuid4

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from dotenv import load_dotenv

from axe_core.paths import project_root, public_dir
from axe_orchestrator import runners
from axe_orchestrator.committee_orchestrator import run_committee
from axe_orchestrator.health import generate_health, write_health
from axe_orchestrator.projector import build_command_center_payload, write_command_center_artifacts

load_dotenv(project_root() / ".env", override=False)

_run_queues: dict[str, asyncio.Queue] = {}


class CommitteeRunRequest(BaseModel):
    candidate_type: str = "position_review"
    api_key: str | None = None


AGENT_RUNNERS: dict[str, Callable[[], int]] = {
    "portfolio": runners.run_portfolio,
    "alpha": runners.run_alpha,
    "news": runners.run_news,
    "specialists": runners.run_specialists,
    "specialists_decide": runners.run_specialists_and_decide,
    "opportunities": runners.run_opportunities,
    "decision": runners.run_decision,
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
        for name in runners.RUN_ALL_ORDER:
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
    api = APIRouter(prefix="/api")

    async def _health_impl() -> JSONResponse:
        pub = public_dir()
        health_path = pub / "health.json"
        if not health_path.exists():
            write_health()
        report = generate_health(pub)
        return JSONResponse(report)

    @app.get("/health")
    async def health_root() -> JSONResponse:
        return await _health_impl()

    @api.get("/health")
    async def health_api() -> JSONResponse:
        return await _health_impl()

    @api.get("/command-center")
    async def command_center_api() -> JSONResponse:
        public = public_dir()
        write_command_center_artifacts(public)
        return JSONResponse(build_command_center_payload(public))

    async def _refresh_impl(target: str) -> JSONResponse:
        if REFRESH_LOCK.locked():
            raise HTTPException(status_code=409, detail="A refresh is already in progress")
        async with REFRESH_LOCK:
            payload = await _run_agent(target)
        write_command_center_artifacts(public_dir())
        return JSONResponse(payload)

    # Primary refresh endpoint (use POST for side effects).
    @app.post("/refresh/{target}")
    async def refresh_post(target: str) -> JSONResponse:
        return await _refresh_impl(target)

    @api.post("/refresh/{target}")
    async def refresh_post_api(target: str) -> JSONResponse:
        return await _refresh_impl(target)

    # Convenience endpoints (older clients/UI may use GET).
    @app.get("/refresh/{target}")
    async def refresh_get(target: str) -> JSONResponse:
        return await _refresh_impl(target)

    @api.get("/refresh/{target}")
    async def refresh_get_api(target: str) -> JSONResponse:
        return await _refresh_impl(target)

    @app.post("/refresh")
    async def refresh_all_post() -> JSONResponse:
        return await _refresh_impl("all")

    @api.post("/refresh")
    async def refresh_all_post_api() -> JSONResponse:
        return await _refresh_impl("all")

    @app.get("/refresh")
    async def refresh_all_get() -> JSONResponse:
        return await _refresh_impl("all")

    @api.get("/refresh")
    async def refresh_all_get_api() -> JSONResponse:
        return await _refresh_impl("all")

    async def _trace_stream_impl(run_id: str, request: Request) -> EventSourceResponse:
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

    @app.get("/trace/stream/{run_id}")
    async def trace_stream(run_id: str, request: Request) -> EventSourceResponse:
        return await _trace_stream_impl(run_id, request)

    @api.get("/trace/stream/{run_id}")
    async def trace_stream_api(run_id: str, request: Request) -> EventSourceResponse:
        return await _trace_stream_impl(run_id, request)

    @api.post("/runs/{ticker}")
    async def start_committee_run(ticker: str, body: CommitteeRunRequest) -> JSONResponse:
        run_id = f"{ticker.upper()}-{uuid4().hex[:8]}"
        queue: asyncio.Queue = asyncio.Queue()
        _run_queues[run_id] = queue
        key = body.api_key or os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY not set")
        asyncio.create_task(
            run_committee(
                ticker=ticker,
                candidate_type=body.candidate_type,
                run_id=run_id,
                queue=queue,
                api_key=key,
            )
        )
        return JSONResponse({"run_id": run_id, "ticker": ticker.upper(), "status": "started"})

    @api.get("/runs/{run_id}/stream")
    async def stream_committee_run(run_id: str, request: Request) -> EventSourceResponse:
        queue = _run_queues.get(run_id)
        if queue is None:
            raise HTTPException(status_code=404, detail=f"run_id not found: {run_id}")

        async def event_generator():
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "{}"}
                    continue
                if event is None:
                    yield {"event": "done", "data": json.dumps({"run_id": run_id})}
                    _run_queues.pop(run_id, None)
                    break
                yield {"event": "event", "data": json.dumps(event)}

        return EventSourceResponse(event_generator(), ping=10)

    app.include_router(api)

    return app


app = create_app()
