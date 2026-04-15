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
