"""`axe-news` CLI: fetch, score, write news-latest.json, emit trace."""
from __future__ import annotations

import asyncio
import json
import os

from axe_core import Tracer
from axe_core.paths import public_dir
from axe_news.feeds import FEEDS, yahoo_ticker_feed
from axe_news.ingest import dedupe, extract_tickers, fetch_feed
from axe_news.pipeline import assemble_report, classify_relevance
from axe_news.scorer import score_item
from axe_news.watchlist import load_watchlist


def _atomic_write_json(path, data) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


async def _fetch_all(feeds) -> tuple[list, list[str]]:
    results = await asyncio.gather(*[fetch_feed(f) for f in feeds], return_exceptions=True)
    items = []
    polled: list[str] = []
    for feed, res in zip(feeds, results):
        polled.append(feed.id)
        if isinstance(res, Exception):
            continue
        items.extend(res)
    return items, polled


def main() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY not set")

    watchlist = load_watchlist()
    held = watchlist  # Held subset — same as watchlist for now; refine when holdings drift from profile.

    tracer = Tracer(agent="axe_news")
    tracer.start()
    tracer.event(step="load_watchlist", thought=f"watchlist has {len(watchlist)} tickers")

    feeds = list(FEEDS) + [yahoo_ticker_feed(t) for t in sorted(watchlist)]
    tracer.event(step="fetch_feeds", thought=f"polling {len(feeds)} feeds", io={"in": {"feed_count": len(feeds)}})

    try:
        raw, polled = asyncio.run(_fetch_all(feeds))
    except Exception as exc:
        tracer.event(step="error", thought=f"fetch failed: {exc}")
        tracer.finalize(status="failed", summary=f"fetch failed: {exc}", artifact_written=None)
        raise

    deduped = dedupe(raw)
    tracer.event(
        step="dedupe",
        thought=f"{len(raw)} raw → {len(deduped)} unique",
        io={"in": {"n": len(raw)}, "out": {"n": len(deduped)}},
    )

    scored = []
    scored_count = 0
    for item in deduped:
        tickers = extract_tickers(item, watchlist)
        relevance = classify_relevance(tickers, held, watchlist)
        if relevance == "none":
            continue  # Skip LLM call when nothing in watchlist mentioned.
        try:
            result = score_item(item, tickers, relevance, api_key=api_key)
        except Exception as exc:
            tracer.event(step="score_error", thought=f"skipping item due to {exc}", io={"in": {"url": item.url}})
            continue
        scored_count += 1
        if result is None:
            continue
        scored.append((item, tickers, relevance, result))

    tracer.event(
        step="score",
        thought=f"scored {scored_count} items via Haiku 4.5",
        io={"out": {"scored": scored_count}},
    )

    from datetime import datetime, timezone
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = assemble_report(scored, sources_polled=polled, items_in=len(raw), generated_at=generated_at)

    out_path = public_dir() / "news-latest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(out_path, report)

    tracer.event(
        step="write_artifact",
        thought=f"wrote {report['items_kept']} items to news-latest.json",
    )
    tracer.finalize(
        status="success",
        summary=f"{len(raw)} in, {report['items_kept']} kept (score>=6)",
        artifact_written="news-latest.json",
    )


if __name__ == "__main__":
    main()
