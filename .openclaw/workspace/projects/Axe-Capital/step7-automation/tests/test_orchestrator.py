"""Unit tests for committee_orchestrator helpers."""
from __future__ import annotations

import asyncio
import json

import pytest

from axe_orchestrator.committee_orchestrator import (
    VALID_ACTIONS,
    _analyst_result_to_events,
    _decision_stage_to_events,
    validate_ceo_action,
)


# ---------------------------------------------------------------------------
# validate_ceo_action
# ---------------------------------------------------------------------------

def test_validate_ceo_action_passthrough():
    for action in VALID_ACTIONS:
        memo = {"action": action, "conviction_1_to_10": 7}
        result = validate_ceo_action(memo)
        assert result["action"] == action
        assert "_action_coerced" not in result


def test_validate_ceo_action_coerces_unknown_to_watch():
    memo = {"action": "YOLO", "thesis": "moon"}
    result = validate_ceo_action(memo)
    assert result["action"] == "WATCH"
    assert result["_action_coerced"] == "YOLO"


def test_validate_ceo_action_coerces_empty_to_watch():
    memo = {"action": ""}
    result = validate_ceo_action(memo)
    assert result["action"] == "WATCH"


def test_validate_ceo_action_case_insensitive():
    memo = {"action": "buy"}
    result = validate_ceo_action(memo)
    assert result["action"] == "BUY"
    assert "_action_coerced" not in result


# ---------------------------------------------------------------------------
# _analyst_result_to_events
# ---------------------------------------------------------------------------

def test_analyst_result_produces_typed_events():
    result = {
        "stage": "fundamental",
        "memo": {
            "thesis": "Revenue growing 15% YoY",
            "key_facts": ["Free cash flow positive", "Margin expanding"],
            "risks": ["Competition heating up"],
            "score_1_to_10": 7,
        },
    }
    events = _analyst_result_to_events(result)
    assert len(events) >= 1

    types = {e["event_type"] for e in events}
    assert "claim" in types

    roles = {e["role"] for e in events}
    assert roles == {"fundamental"}

    for ev in events:
        assert "confidence" in ev
        assert 0.0 <= ev["confidence"] <= 1.0
        assert "content" in ev
        assert isinstance(ev["content"], str)


def test_analyst_result_fallback_when_empty_memo():
    result = {"stage": "macro", "memo": {}}
    events = _analyst_result_to_events(result)
    assert len(events) == 1
    assert events[0]["event_type"] == "claim"
    assert "macro" in events[0]["content"]


# ---------------------------------------------------------------------------
# _decision_stage_to_events
# ---------------------------------------------------------------------------

def test_decision_stage_bull_produces_claim():
    memo = {"thesis": "Strong tailwinds", "catalysts": ["Rate cut", "AI surge"]}
    events = _decision_stage_to_events("bull", memo)
    assert any(e["event_type"] == "claim" for e in events)
    assert all(e["role"] == "bull" for e in events)


def test_decision_stage_bear_produces_objection():
    memo = {"thesis": "Valuation stretched", "risks": ["Margin compression", "FX headwind"]}
    events = _decision_stage_to_events("bear", memo)
    assert any(e["event_type"] == "objection" for e in events)


def test_decision_stage_cro_includes_gate():
    memo = {"gate": "APPROVED", "notes": "Within risk limits"}
    events = _decision_stage_to_events("cro", memo)
    assert len(events) == 1
    assert "APPROVED" in events[0]["content"]
    assert events[0]["role"] == "cro"


def test_decision_stage_ceo_produces_decision_event():
    memo = {
        "action": "ADD",
        "conviction_1_to_10": 8,
        "thesis": "Thesis intact, add on dip",
    }
    events = _decision_stage_to_events("ceo", memo)
    assert len(events) == 1
    ev = events[0]
    assert ev["event_type"] == "decision"
    assert ev["role"] == "ceo"
    assert "ADD" in ev["content"]
    assert ev["action"] == "ADD"
    assert pytest.approx(ev["confidence"], abs=0.05) == 0.8


def test_decision_stage_ceo_coerces_bad_action():
    memo = {"action": "YOLO", "conviction_1_to_10": 5, "thesis": "No idea"}
    events = _decision_stage_to_events("ceo", memo)
    assert events[0]["action"] == "WATCH"


# ---------------------------------------------------------------------------
# run_committee emits error event on failure
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="function")
async def test_orchestrator_emits_error_event_on_failure(monkeypatch):
    """If run_parallel_analysis raises, the queue should get an error event then None."""
    import axe_orchestrator.committee_orchestrator as orch

    async def _bad_analysis(*args, **kwargs):
        raise RuntimeError("simulated analyst failure")

    monkeypatch.setattr(orch, "run_parallel_analysis", _bad_analysis)

    # Also patch _build_bundle so it doesn't hit yfinance
    async def _fake_bundle(ticker, portfolio_ctx):
        return {"ticker": ticker, "prices": {"rows": []}}

    monkeypatch.setattr(orch, "_build_bundle", _fake_bundle)

    queue: asyncio.Queue = asyncio.Queue()
    await orch.run_committee(
        ticker="TEST",
        candidate_type="new_position",
        run_id="test-run-001",
        queue=queue,
        api_key="fake-key",
    )

    events = []
    while not queue.empty():
        events.append(await queue.get())

    error_events = [e for e in events if e is not None and e.get("event_type") == "error"]
    assert len(error_events) == 1
    assert "simulated analyst failure" in error_events[0]["content"]
    assert events[-1] is None  # sentinel present
