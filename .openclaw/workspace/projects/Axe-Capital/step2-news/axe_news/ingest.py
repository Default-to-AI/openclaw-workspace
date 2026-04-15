"""RSS fetch, parse, dedupe, ticker extraction."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

import feedparser
import httpx

from axe_news.feeds import Feed


@dataclass
class RawItem:
    title: str
    url: str
    source: str
    published_at: str
    summary: str


USER_AGENT = "AxeCapitalNews/0.1 (research; contact: roberttiger9@gmail.com)"
TICKER_RE = re.compile(r"\b([A-Z]{2,5})\b")


def item_id(item: RawItem) -> str:
    return hashlib.sha1(item.url.encode("utf-8")).hexdigest()


def _to_iso(entry) -> str:
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None) or entry.get(key) if isinstance(entry, dict) else getattr(entry, key, None)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_feed_bytes(raw: bytes, feed: Feed) -> list[RawItem]:
    parsed = feedparser.parse(raw)
    items: list[RawItem] = []
    for entry in parsed.entries:
        items.append(
            RawItem(
                title=(entry.get("title") or "").strip(),
                url=(entry.get("link") or "").strip(),
                source=feed.id,
                published_at=_to_iso(entry),
                summary=(entry.get("summary") or entry.get("description") or "").strip(),
            )
        )
    return items


async def fetch_feed(feed: Feed, timeout: float = 15.0) -> list[RawItem]:
    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": USER_AGENT}) as client:
        resp = await client.get(feed.url)
        resp.raise_for_status()
        return parse_feed_bytes(resp.content, feed)


def dedupe(items: Iterable[RawItem]) -> list[RawItem]:
    seen: set[str] = set()
    out: list[RawItem] = []
    for item in items:
        key = item_id(item)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def extract_tickers(item: RawItem, watchlist: set[str]) -> list[str]:
    """Extract ALL-CAPS tokens that match the portfolio/watchlist set.

    Restricting to the watchlist avoids false positives on English words
    that happen to be in caps (THE, CEO, NEWS, etc.). Unknown tickers are
    intentionally dropped — the user told us what matters.
    """
    text = f"{item.title} {item.summary}"
    found: list[str] = []
    for token in TICKER_RE.findall(text):
        if token in watchlist and token not in found:
            found.append(token)
    return found
