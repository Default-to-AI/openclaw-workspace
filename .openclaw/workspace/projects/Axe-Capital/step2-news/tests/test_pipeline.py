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
