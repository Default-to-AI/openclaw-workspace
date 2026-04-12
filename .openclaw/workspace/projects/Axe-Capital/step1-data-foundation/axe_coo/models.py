from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceStatus(BaseModel):
    name: str
    ok: bool
    fetched_at: datetime
    stale: bool = False
    error: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class PriceHistory(BaseModel):
    interval: str
    period: str
    currency: str | None = None
    rows: list[dict[str, Any]]  # [{ts, open, high, low, close, volume}]


class FinancialSnapshot(BaseModel):
    currency: str | None = None
    market_cap: float | None = None
    shares_outstanding: float | None = None
    trailing_pe: float | None = None
    forward_pe: float | None = None
    price_to_book: float | None = None
    profit_margins: float | None = None
    operating_margins: float | None = None
    return_on_equity: float | None = None
    total_cash: float | None = None
    total_debt: float | None = None
    free_cashflow: float | None = None
    revenue_ttm: float | None = None


class EdgarFiling(BaseModel):
    form: str
    filing_date: str | None = None
    report_date: str | None = None
    accession_number: str | None = None
    primary_document: str | None = None
    filing_url: str | None = None
    description: str | None = None


class NewsItem(BaseModel):
    title: str
    url: str
    source: str | None = None
    published_at: str | None = None
    description: str | None = None


class RedditPost(BaseModel):
    subreddit: str
    id: str
    title: str
    url: str | None = None
    created_utc: float | None = None
    score: int | None = None
    num_comments: int | None = None
    author: str | None = None


class FredSeriesPoint(BaseModel):
    date: str
    value: float | None


class TickerBundle(BaseModel):
    ticker: str
    company_name: str | None = None
    fetched_at: datetime
    sources: list[SourceStatus]

    prices: PriceHistory | None = None
    financial_snapshot: FinancialSnapshot | None = None
    earnings_dates: list[str] = Field(default_factory=list)

    sec_filings: list[EdgarFiling] = Field(default_factory=list)
    news: list[NewsItem] = Field(default_factory=list)
    macro: dict[str, list[FredSeriesPoint]] = Field(default_factory=dict)
    reddit: list[RedditPost] = Field(default_factory=list)
    options_flow: dict[str, Any] | None = None

    freshness: dict[str, Any] = Field(default_factory=dict)


class FreshnessPolicy(BaseModel):
    prices_max_age_seconds: int = 60 * 60 * 12
    fundamentals_max_age_seconds: int = 60 * 60 * 24
    news_max_age_seconds: int = 60 * 30
    sec_max_age_seconds: int = 60 * 60 * 6
    macro_max_age_seconds: int = 60 * 60 * 6
    reddit_max_age_seconds: int = 60 * 30
    options_flow_max_age_seconds: int = 60 * 30


class OutputFormat(BaseModel):
    kind: Literal["json"] = "json"
