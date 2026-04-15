"""Static catalog of RSS feeds to poll."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Feed:
    id: str       # short stable id used in trace + sources_polled
    url: str
    category: str  # "wire" | "regulatory" | "ticker"


FEEDS: tuple[Feed, ...] = (
    Feed("reuters-biz", "https://feeds.reuters.com/reuters/businessNews", "wire"),
    Feed("bloomberg-mkts", "https://feeds.bloomberg.com/markets/news.rss", "wire"),
    Feed("sec-edgar-8k", "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=8-K&dateb=&owner=include&count=40&output=atom", "regulatory"),
)


def yahoo_ticker_feed(ticker: str) -> Feed:
    return Feed(
        id=f"yahoo-ticker:{ticker}",
        url=f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        category="ticker",
    )
