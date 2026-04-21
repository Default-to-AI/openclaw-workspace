"""Committee pipeline orchestrator — runs research + debate and streams events via asyncio.Queue."""
from __future__ import annotations

import asyncio
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yfinance

from axe_core.llm import MODEL_ANALYST, chat_json
from axe_core.paths import project_root, public_dir
from axe_coo.step2_analysis import run_parallel_analysis
from axe_coo.step3_decision import run_step3_decision

VALID_ACTIONS = {"BUY", "ADD", "HOLD", "TRIM", "SELL", "TIGHTEN_STOP", "LOOSEN_STOP", "REBALANCE", "WATCH"}

PLAYBOOK_SYSTEM = """You are Axe Capital's Position Manager. The CEO has issued a decision. Build a concrete price-level playbook — specific levels, specific conditional actions.

Identify key price levels from the technical analysis (support, resistance, moving averages, prior highs/lows). For each level, specify what action to take when price reaches it.

Tailor the playbook to the CEO action:
  HOLD           — stop level, target, watch levels, what triggers ADD vs TRIM vs SELL
  BUY / ADD      — entry zone, stop-loss, scaling plan, profit-take tiers, thesis invalidation trigger
  SELL / TRIM    — exit levels, partial vs full exit, re-entry conditions, what would flip the view
  TIGHTEN_STOP   — exact new stop number, rationale, what happens if triggered
  LOOSEN_STOP    — new wider stop, why volatility warrants it, revised risk amount
  WATCH          — exact price or event that triggers action, what to look for, monitoring cadence
  REBALANCE      — target weight, acceptable price window for execution, what changes the plan

Return JSON only with keys:
  action (string),
  stop_loss_level (number or null),
  target_price (number or null),
  key_levels (list, max 5, each: {price, label, action, trigger}),
  if_price_rises (string, 1-2 sentences),
  if_price_falls (string, 1-2 sentences),
  if_sideways (string, 1-2 sentences),
  review_trigger (string — when to re-evaluate),
  sizing_note (string or null)"""


def validate_ceo_action(ceo: dict) -> dict:
    action = (ceo.get("action") or "").upper().strip()
    if action not in VALID_ACTIONS:
        ceo["_action_coerced"] = action
        ceo["action"] = "WATCH"
    else:
        ceo["action"] = action
    return ceo


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json_file(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _portfolio_context_for(ticker: str) -> dict | None:
    pub = public_dir()
    portfolio = _load_json_file(pub / "portfolio.json")
    position_state = _load_json_file(pub / "position-state.json")

    symbol = ticker.upper()
    position = next((p for p in portfolio.get("positions", []) if p.get("symbol") == symbol), None)
    if position is None:
        return None

    state = (position_state.get("positions") or {}).get(symbol, {})
    return {
        "symbol": symbol,
        "shares": position.get("shares"),
        "weight_pct": position.get("weight_pct"),
        "cost_basis": position.get("cost_basis"),
        "avg_price": position.get("avg_price"),
        "last_price": position.get("last_price"),
        "unrealized_pl": position.get("unrealized_pl"),
        "unrealized_pl_pct": position.get("unrealized_pl_pct"),
        "stop_loss": state.get("stop_loss") or position.get("stop_loss_level"),
        "target_price": state.get("target_price"),
        "thesis": state.get("thesis"),
        "alert_status": position.get("alert_status"),
    }


def _news_for_ticker(ticker: str) -> list[dict]:
    pub = public_dir()
    news_data = _load_json_file(pub / "news-latest.json")
    articles = news_data.get("articles") or news_data.get("items") or []
    symbol = ticker.upper()
    matched = []
    for a in articles:
        tickers = a.get("tickers_mentioned") or a.get("tickers") or []
        if symbol in [t.upper() for t in tickers]:
            matched.append({
                "title": a.get("title"),
                "published_at": a.get("published_at") or a.get("date"),
                "source": a.get("source"),
                "summary": a.get("summary") or a.get("description"),
                "sentiment": a.get("sentiment"),
            })
    return matched[:10]


async def _build_bundle(ticker: str, portfolio_ctx: dict | None) -> dict:
    loop = asyncio.get_running_loop()

    def _fetch_yf() -> tuple[dict, list[dict]]:
        stock = yfinance.Ticker(ticker)
        info = stock.info or {}
        hist = stock.history(period="6mo", interval="1d")
        rows = []
        for row in hist.itertuples():
            rows.append({
                "date": str(row.Index.date()),
                "open": float(row.Open) if row.Open else None,
                "high": float(row.High) if row.High else None,
                "low": float(row.Low) if row.Low else None,
                "close": float(row.Close) if row.Close else None,
                "volume": float(row.Volume) if row.Volume else None,
            })
        return info, rows

    info, price_rows = await loop.run_in_executor(None, _fetch_yf)
    news = _news_for_ticker(ticker)

    bundle: dict[str, Any] = {
        "ticker": ticker.upper(),
        "fetched_at": _utc_now(),
        "prices": {"rows": price_rows},
        "financial_snapshot": info,
        "earnings_dates": [],
        "sec_filings": [],
        "news": news,
        "reddit": [],
        "options_flow": None,
        "macro": {},
    }

    if portfolio_ctx:
        bundle["portfolio_context"] = portfolio_ctx

    return bundle


def _analyst_result_to_events(result: dict) -> list[dict]:
    stage = result.get("analyst") or result.get("stage") or "unknown"
    memo = result.get("memo") or {}
    events = []
    confidence = min(1.0, (memo.get("score_1_to_10") or memo.get("confidence_1_to_10") or 5) / 10)

    # Primary claim
    primary = (
        memo.get("thesis")
        or memo.get("macro_thesis")
        or memo.get("narrative_summary")
        or memo.get("setup")
        or memo.get("trend")
    )
    if primary:
        events.append({
            "role": stage,
            "event_type": "claim",
            "content": str(primary),
            "confidence": confidence,
            "sources": ["yfinance"],
        })

    # Key evidence items
    evidence_fields = ["key_facts", "catalysts", "tailwinds", "top_catalysts", "headline_takeaways"]
    for field in evidence_fields:
        items = memo.get(field) or []
        if isinstance(items, list):
            for item in items[:3]:
                if item:
                    events.append({
                        "role": stage,
                        "event_type": "evidence",
                        "content": str(item),
                        "confidence": confidence,
                        "sources": [],
                    })
            break

    # Risks as objections
    risks = memo.get("risks") or memo.get("headwinds") or memo.get("top_risks") or []
    if isinstance(risks, list):
        for risk in risks[:2]:
            if risk:
                events.append({
                    "role": stage,
                    "event_type": "objection",
                    "content": str(risk),
                    "confidence": max(0.1, confidence - 0.2),
                    "sources": [],
                })

    if not events:
        events.append({
            "role": stage,
            "event_type": "claim",
            "content": f"{stage} analysis complete",
            "confidence": confidence,
            "sources": [],
        })

    return events


def _decision_stage_to_events(stage_name: str, memo: dict) -> list[dict]:
    events = []

    if stage_name == "bull":
        thesis = memo.get("thesis") or memo.get("summary")
        if thesis:
            events.append({"role": "bull", "event_type": "claim", "content": str(thesis), "confidence": 0.7, "sources": []})
        for cat in (memo.get("catalysts") or memo.get("key_catalysts") or [])[:3]:
            events.append({"role": "bull", "event_type": "evidence", "content": str(cat), "confidence": 0.7, "sources": []})

    elif stage_name == "bear":
        thesis = memo.get("thesis") or memo.get("summary") or memo.get("kill_shots")
        if isinstance(thesis, list):
            thesis = thesis[0] if thesis else None
        if thesis:
            events.append({"role": "bear", "event_type": "claim", "content": str(thesis), "confidence": 0.6, "sources": []})
        for risk in (memo.get("risks") or memo.get("kill_shots") or [])[:3]:
            events.append({"role": "bear", "event_type": "objection", "content": str(risk), "confidence": 0.6, "sources": []})

    elif stage_name in ("debate", "cio"):
        summary = memo.get("summary") or memo.get("verdict") or memo.get("debate_summary")
        if summary:
            events.append({"role": "debate", "event_type": "claim", "content": str(summary), "confidence": 0.65, "sources": []})

    elif stage_name == "cro":
        gate = memo.get("gate", "UNKNOWN")
        rationale = memo.get("veto_rationale") or memo.get("notes") or f"Risk gate: {gate}"
        events.append({"role": "cro", "event_type": "claim", "content": f"[{gate}] {rationale}", "confidence": 1.0, "sources": []})

    elif stage_name == "ceo":
        memo = validate_ceo_action(memo)
        action = memo.get("action", "WATCH")
        conviction = memo.get("conviction_1_to_10") or memo.get("conviction") or 5
        confidence = min(1.0, float(conviction) / 10)
        thesis = memo.get("thesis") or memo.get("rationale") or "Decision complete"
        events.append({
            "role": "ceo",
            "event_type": "decision",
            "content": f"[{action}] {thesis}",
            "confidence": confidence,
            "sources": [],
            "action": action,
            "memo": memo,
        })

    if not events:
        events.append({
            "role": stage_name,
            "event_type": "claim",
            "content": f"{stage_name} stage complete",
            "confidence": 0.5,
            "sources": [],
        })

    return events


def _persist_run(ticker: str, candidate_type: str, step2: dict, decision: dict, run_id: str, playbook: dict | None = None) -> None:
    pub = public_dir()
    ts = _utc_now().replace(":", "-")
    trace_path = pub / "traces" / f"committee-{ticker.lower()}-{ts}.json"
    trace_path.parent.mkdir(parents=True, exist_ok=True)

    ceo_memo = (decision.get("ceo") or {}).get("memo") or {}
    validate_ceo_action(ceo_memo)

    artifact = {
        "run_id": run_id,
        "ticker": ticker.upper(),
        "candidate_type": candidate_type,
        "generated_at": _utc_now(),
        "status": "success",
        "step2_analysis": step2,
        "decision": decision,
        "ceo_action": ceo_memo.get("action", "WATCH"),
        "ceo_conviction": ceo_memo.get("conviction_1_to_10") or ceo_memo.get("conviction"),
        "ceo_thesis": ceo_memo.get("thesis"),
        "playbook": playbook or {},
    }
    trace_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")

    # Also write decision-latest.json for existing dashboard panels
    latest_path = pub / "decision-latest.json"
    latest_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")


async def _run_playbook(
    decision: dict,
    step2: dict,
    portfolio_ctx: dict | None,
    api_key: str,
) -> dict:
    ceo_memo = (decision.get("ceo") or {}).get("memo") or {}
    technical_memo = next(
        (r.get("memo") for r in (step2.get("results") or []) if r.get("analyst") == "technical"),
        {},
    )
    payload = {
        "ticker": step2.get("ticker"),
        "ceo_decision": ceo_memo,
        "technical_analysis": technical_memo,
        "portfolio_context": portfolio_ctx,
    }
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: chat_json(
            api_key=api_key,
            model=MODEL_ANALYST,
            system=PLAYBOOK_SYSTEM,
            user=payload,
            max_tokens=900,
        ),
    )


async def run_committee(
    *,
    ticker: str,
    candidate_type: str,
    run_id: str,
    queue: asyncio.Queue,
    api_key: str,
) -> None:
    """Full committee pipeline. Writes events to queue as each stage completes. Puts None sentinel at end."""
    try:
        portfolio_ctx = _portfolio_context_for(ticker)
        effective_candidate_type = candidate_type if portfolio_ctx else "new_position"

        # Announce start
        await queue.put({
            "role": "orchestrator",
            "event_type": "claim",
            "content": f"Starting committee for {ticker.upper()} ({effective_candidate_type})",
            "confidence": 1.0,
            "sources": [],
        })

        # Build data bundle
        bundle = await _build_bundle(ticker, portfolio_ctx)

        # Parallel analyst phase
        investor_profile_text = (project_root() / "INVESTOR_PROFILE.md").read_text(encoding="utf-8")
        step2 = await run_parallel_analysis(bundle, api_key, timeout_seconds=120.0)

        # Stream analyst events
        for result in step2.get("results") or []:
            for ev in _analyst_result_to_events(result):
                await queue.put(ev)

        # Decision pipeline
        decision = await run_step3_decision(
            step2_analysis=step2,
            investor_profile_text=investor_profile_text,
            api_key=api_key,
            timeout_seconds=180.0,
        )

        # Stream decision stage events in order
        for stage_name in ("bull", "bear", "debate", "cro", "ceo"):
            stage = decision.get(stage_name) or {}
            if not isinstance(stage, dict):
                stage = {}
            memo = stage.get("memo") or {}
            if not isinstance(memo, dict):
                memo = {}
            for ev in _decision_stage_to_events(stage_name, memo):
                await queue.put(ev)

        # Playbook stage — conditional price-level game plan
        playbook = await _run_playbook(decision, step2, portfolio_ctx, api_key)
        stop = playbook.get("stop_loss_level")
        target = playbook.get("target_price")
        action = playbook.get("action", "")
        parts = [f"Action: {action}"] if action else []
        if stop:
            parts.append(f"Stop: ${stop:,.2f}")
        if target:
            parts.append(f"Target: ${target:,.2f}")
        await queue.put({
            "role": "playbook",
            "event_type": "playbook",
            "content": " · ".join(parts) or "Position playbook",
            "confidence": 1.0,
            "sources": [],
            "memo": playbook,
        })

        _persist_run(ticker, effective_candidate_type, step2, decision, run_id, playbook)

    except Exception as exc:
        await queue.put({
            "role": "orchestrator",
            "event_type": "error",
            "content": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
            "confidence": 0.0,
            "sources": [],
        })
    finally:
        await queue.put(None)
