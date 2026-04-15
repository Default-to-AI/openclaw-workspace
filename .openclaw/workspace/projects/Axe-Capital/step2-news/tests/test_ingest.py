from __future__ import annotations

from pathlib import Path

import pytest

from axe_news.feeds import Feed
from axe_news.ingest import (
    RawItem,
    dedupe,
    extract_tickers,
    fetch_feed,
    item_id,
    parse_feed_bytes,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_feed_bytes_returns_items():
    raw = (FIXTURES / "sample-reuters.xml").read_bytes()
    feed = Feed("reuters-biz", "https://x", "wire")
    items = parse_feed_bytes(raw, feed)
    assert len(items) == 3
    assert items[0].title.startswith("MSFT faces")
    assert items[0].source == "reuters-biz"
    assert items[0].url == "https://reuters.example/msft-antitrust"


def test_item_id_is_stable_sha1_of_url():
    i1 = RawItem(title="t1", url="https://x", source="s", published_at="2026-04-15T00:00:00Z", summary="")
    i2 = RawItem(title="t2", url="https://x", source="s", published_at="2026-04-15T01:00:00Z", summary="")
    assert item_id(i1) == item_id(i2)
    assert len(item_id(i1)) == 40  # sha1 hex


def test_dedupe_keeps_first_occurrence():
    i1 = RawItem(title="first", url="https://a", source="s", published_at="2026-04-15T00:00:00Z", summary="")
    dup = RawItem(title="dup", url="https://a", source="s2", published_at="2026-04-15T01:00:00Z", summary="")
    i3 = RawItem(title="third", url="https://b", source="s", published_at="2026-04-15T02:00:00Z", summary="")
    out = dedupe([i1, dup, i3])
    assert [it.url for it in out] == ["https://a", "https://b"]


def test_extract_tickers_finds_caps_tokens_from_title_and_summary():
    item = RawItem(
        title="MSFT faces DOJ probe",
        url="https://x",
        source="reuters-biz",
        published_at="2026-04-15T00:00:00Z",
        summary="Microsoft and GOOG cloud bundling. Also mentions AAPL.",
    )
    watchlist = {"MSFT", "GOOG", "AAPL", "RTX", "ASML"}
    tickers = extract_tickers(item, watchlist)
    assert set(tickers) == {"MSFT", "GOOG", "AAPL"}


def test_extract_tickers_ignores_common_english_caps_tokens():
    item = RawItem(
        title="THE CEO OF MSFT WILL SPEAK TODAY",
        url="https://x",
        source="s",
        published_at="2026-04-15T00:00:00Z",
        summary="",
    )
    tickers = extract_tickers(item, {"MSFT"})
    # Common words (THE, CEO, OF, WILL, TODAY) are not in the watchlist, so they're filtered
    assert tickers == ["MSFT"]


@pytest.mark.asyncio
async def test_fetch_feed_uses_httpx_client(monkeypatch):
    raw = (FIXTURES / "sample-reuters.xml").read_bytes()
    feed = Feed("reuters-biz", "https://x", "wire")

    class FakeResp:
        status_code = 200
        content = raw

        def raise_for_status(self):
            pass

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

        async def get(self, url, **kwargs):
            return FakeResp()

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", lambda **k: FakeClient())
    items = await fetch_feed(feed)
    assert len(items) == 3
