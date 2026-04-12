from __future__ import annotations

from dataclasses import dataclass

import httpx

from axe_coo.models import NewsItem
from axe_coo.vendors import ddg_search as ddg_vendor


@dataclass
class NewsFetchResult:
    items: list[NewsItem]
    provider: str | None
    used_key: bool
    used_fallback: bool
    warning: str | None = None


def _normalize_news_item(item: dict, *, provider: str) -> NewsItem | None:
    title = item.get("title") or item.get("name") or item.get("body")
    url = item.get("url") or item.get("href")
    if not title or not url:
        return None

    source = item.get("source")
    if isinstance(source, dict):
        source = source.get("name") or source.get("id")

    return NewsItem(
        title=title,
        url=url,
        source=source or provider,
        published_at=item.get("publishedAt") or item.get("date") or item.get("published_at"),
        description=item.get("description") or item.get("body") or item.get("snippet"),
    )


def fetch_newsapi(ticker: str, api_key: str | None, timeout: float = 10.0) -> NewsFetchResult:
    if not api_key:
        return NewsFetchResult(items=[], provider="newsapi", used_key=False, used_fallback=False)

    q = ticker
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
    }
    headers = {"X-Api-Key": api_key}

    with httpx.Client(timeout=timeout) as client:
        r = client.get(url, params=params, headers=headers)
        r.raise_for_status()
        data = r.json() or {}

    out: list[NewsItem] = []
    for article in (data.get("articles") or [])[:20]:
        normalized = _normalize_news_item(article, provider="newsapi")
        if normalized:
            out.append(normalized)

    return NewsFetchResult(items=out, provider="newsapi", used_key=True, used_fallback=False)


def fetch_ddg_news(ticker: str, timeout: float = 10.0, max_results: int = 20) -> NewsFetchResult:
    DDGS = ddg_vendor._load_ddgs()
    query = f"{ticker} stock"
    ddgs = DDGS(timeout=timeout, verify=True)
    results = list(
        ddg_vendor._iter_results(
            ddgs,
            "news",
            query,
            region="us-en",
            safesearch="moderate",
            timelimit="m",
            max_results=max_results,
            backend="auto",
        )
    )

    out: list[NewsItem] = []
    for item in results[:max_results]:
        normalized = _normalize_news_item(item, provider="duckduckgo")
        if normalized:
            out.append(normalized)

    return NewsFetchResult(
        items=out,
        provider="duckduckgo",
        used_key=False,
        used_fallback=True,
    )


def fetch_news_with_fallback(ticker: str, api_key: str | None, timeout: float = 10.0) -> NewsFetchResult:
    primary_warning: str | None = None
    try:
        primary = fetch_newsapi(ticker, api_key=api_key, timeout=timeout)
        if primary.items:
            return primary
        primary_warning = "NewsAPI returned zero items"
    except Exception as exc:
        primary_warning = f"NewsAPI failed: {exc}"

    try:
        fallback = fetch_ddg_news(ticker, timeout=timeout)
        fallback.used_key = bool(api_key)
        fallback.warning = primary_warning
        return fallback
    except Exception as exc:
        warning = primary_warning or f"DuckDuckGo failed: {exc}"
        if primary_warning:
            warning = f"{primary_warning}; DuckDuckGo failed: {exc}"
        return NewsFetchResult(
            items=[],
            provider=None,
            used_key=bool(api_key),
            used_fallback=True,
            warning=warning,
        )
