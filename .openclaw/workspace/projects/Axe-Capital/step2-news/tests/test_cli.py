from __future__ import annotations

import json

from axe_news import cli as news_cli
from axe_news.ingest import RawItem
from axe_news.scorer import ImpactScore
from axe_core import trace as trace_mod


def test_cli_writes_news_latest_and_trace(tmp_path, monkeypatch):
    (tmp_path / "traces").mkdir(parents=True)
    monkeypatch.setattr(trace_mod, "_public_dir", lambda: tmp_path)
    monkeypatch.setattr(news_cli, "public_dir", lambda: tmp_path)

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setattr(news_cli, "load_watchlist", lambda: {"MSFT"})

    items = [
        RawItem(title="MSFT probe", url="https://a", source="reuters-biz", published_at="2026-04-15T00:00:00Z", summary="DOJ opens inquiry into MSFT"),
        RawItem(title="weather update", url="https://b", source="reuters-biz", published_at="2026-04-15T00:00:00Z", summary="nothing relevant"),
    ]

    async def fake_fetch_all(feeds):
        return items, [f.id for f in feeds]

    monkeypatch.setattr(news_cli, "_fetch_all", fake_fetch_all)

    def fake_score(item, tickers, relevance, api_key):
        return ImpactScore(8, "big", "consider trim", "held")

    monkeypatch.setattr(news_cli, "score_item", fake_score)

    news_cli.main()

    report = json.loads((tmp_path / "news-latest.json").read_text())
    assert report["items_kept"] == 1
    assert report["items"][0]["title"] == "MSFT probe"

    index = json.loads((tmp_path / "traces" / "index.json").read_text())
    assert index["runs"][0]["agent"] == "axe_news"
    assert index["runs"][0]["artifact_written"] == "news-latest.json"
    assert index["runs"][0]["status"] == "success"
