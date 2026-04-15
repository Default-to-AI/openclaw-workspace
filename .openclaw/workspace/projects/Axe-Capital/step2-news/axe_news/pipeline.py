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
