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
