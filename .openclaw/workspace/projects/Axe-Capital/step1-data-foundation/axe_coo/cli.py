from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

from axe_coo.connectors.fred import fetch_fred_series
from axe_coo.connectors.newsapi import NewsFetchResult, fetch_news_with_fallback
from axe_coo.connectors.options_flow import OptionsFlowResult, fetch_options_flow
from axe_coo.connectors.reddit import fetch_reddit_posts
from axe_coo.connectors.sec_edgar import fetch_edgar_bundle
from axe_coo.connectors.yfinance_conn import fetch_yfinance_bundle
from axe_coo.models import FreshnessPolicy, SourceStatus, TickerBundle
from axe_coo.normalize.freshness import build_freshness_report, is_stale
from axe_coo.util.env import load_project_env, missing_required_env_keys, print_env_status_table
from axe_coo.util.time import now_utc

MACRO_SERIES = ["DFF", "CPIAUCSL", "DGS10", "VIXCLS"]


def _warn(message: str | None) -> None:
    if message:
        print(f"Warning: {message}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(prog="axe-coo-bundle")
    ap.add_argument("ticker")
    ap.add_argument("--out", default="-")
    ap.add_argument("--period", default="6mo")
    ap.add_argument("--interval", default="1d")
    args = ap.parse_args()

    env_path = load_project_env()
    print_env_status_table()
    missing_keys = missing_required_env_keys()
    if missing_keys:
        print(
            "COO startup blocked: missing required environment keys: " + ", ".join(missing_keys),
            file=sys.stderr,
        )
        print(f"Fill them in at: {env_path}", file=sys.stderr)
        raise SystemExit(2)

    policy = FreshnessPolicy()
    sources: list[SourceStatus] = []
    fetched_at_by_source: dict[str, datetime] = {}

    # yfinance
    yf_fetched = now_utc()
    try:
        yf_res = fetch_yfinance_bundle(args.ticker, period=args.period, interval=args.interval)
        sources.append(
            SourceStatus(
                name="prices",
                ok=yf_res.prices is not None,
                fetched_at=yf_fetched,
                stale=False,
            )
        )
        sources.append(
            SourceStatus(
                name="fundamentals",
                ok=yf_res.snapshot is not None,
                fetched_at=yf_fetched,
                stale=False,
            )
        )
        fetched_at_by_source["prices"] = yf_fetched
        fetched_at_by_source["fundamentals"] = yf_fetched
    except Exception as exc:
        sources.append(SourceStatus(name="prices", ok=False, fetched_at=yf_fetched, error=str(exc)))
        sources.append(SourceStatus(name="fundamentals", ok=False, fetched_at=yf_fetched, error=str(exc)))
        yf_res = None

    # SEC EDGAR
    sec_fetched = now_utc()
    try:
        sec_res = fetch_edgar_bundle(args.ticker)
        sources.append(
            SourceStatus(
                name="sec",
                ok=len(sec_res.filings) > 0,
                fetched_at=sec_fetched,
                stale=False,
                meta={"cik": sec_res.cik},
            )
        )
        fetched_at_by_source["sec"] = sec_fetched
    except Exception as exc:
        sources.append(SourceStatus(name="sec", ok=False, fetched_at=sec_fetched, error=str(exc)))
        sec_res = None

    # NewsAPI primary, DuckDuckGo fallback
    news_fetched = now_utc()
    try:
        news_key = os.getenv("NEWSAPI_KEY")
        news_res: NewsFetchResult = fetch_news_with_fallback(args.ticker, api_key=news_key)
        _warn(news_res.warning)
        sources.append(
            SourceStatus(
                name="news",
                ok=len(news_res.items) > 0,
                fetched_at=news_fetched,
                stale=False,
                error=(news_res.warning if len(news_res.items) == 0 else None),
                meta={
                    "provider": news_res.provider,
                    "used_key": news_res.used_key,
                    "used_fallback": news_res.used_fallback,
                },
            )
        )
        fetched_at_by_source["news"] = news_fetched
    except Exception as exc:
        sources.append(SourceStatus(name="news", ok=False, fetched_at=news_fetched, error=str(exc)))
        news_res = NewsFetchResult(items=[], provider=None, used_key=bool(os.getenv("NEWSAPI_KEY")), used_fallback=False, warning=str(exc))

    # FRED
    macro_fetched = now_utc()
    macro: dict[str, list] = {}
    macro_errors: dict[str, str] = {}
    fred_key = os.getenv("FRED_API_KEY")
    for sid in MACRO_SERIES:
        try:
            fr = fetch_fred_series(sid, api_key=fred_key)
            macro[sid] = fr.points
        except Exception as exc:
            macro_errors[sid] = str(exc)
            _warn(f"macro series {sid} failed: {exc}")

    sources.append(
        SourceStatus(
            name="macro",
            ok=len(macro_errors) == 0 and len(macro) == len(MACRO_SERIES),
            fetched_at=macro_fetched,
            stale=False,
            error=("; ".join(f"{sid}: {err}" for sid, err in macro_errors.items()) or None),
            meta={
                "used_key": bool(fred_key),
                "series": list(macro.keys()),
                "failed_series": macro_errors,
            },
        )
    )
    fetched_at_by_source["macro"] = macro_fetched

    # Reddit stays optional, never blocks startup
    reddit_fetched = now_utc()
    try:
        rr = fetch_reddit_posts(
            args.ticker,
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
        )
        sources.append(
            SourceStatus(
                name="reddit",
                ok=len(rr.posts) > 0 or not rr.used_creds,
                fetched_at=reddit_fetched,
                stale=False,
                meta={"used_creds": rr.used_creds},
            )
        )
        fetched_at_by_source["reddit"] = reddit_fetched
    except Exception as exc:
        sources.append(SourceStatus(name="reddit", ok=False, fetched_at=reddit_fetched, error=str(exc)))
        rr = None

    # Options flow via vendored Stock Market Pro UW helper
    options_fetched = now_utc()
    options_res: OptionsFlowResult = fetch_options_flow(args.ticker)
    _warn(options_res.warning)
    sources.append(
        SourceStatus(
            name="options_flow",
            ok=options_res.data is not None,
            fetched_at=options_fetched,
            stale=False,
            error=(options_res.warning if options_res.data is None else None),
        )
    )
    fetched_at_by_source["options_flow"] = options_fetched

    bundle_time = now_utc()
    for source in sources:
        max_age_seconds = getattr(policy, f"{source.name}_max_age_seconds", None)
        if max_age_seconds is None:
            source.stale = False
        else:
            source.stale = is_stale(bundle_time, source.fetched_at, max_age_seconds)

    bundle = TickerBundle(
        ticker=args.ticker.upper(),
        company_name=None,
        fetched_at=bundle_time,
        sources=sources,
        prices=(yf_res.prices if yf_res else None),
        financial_snapshot=(yf_res.snapshot if yf_res else None),
        earnings_dates=(yf_res.earnings_dates if yf_res else []),
        sec_filings=(sec_res.filings if sec_res else []),
        news=news_res.items,
        macro=macro,
        reddit=(rr.posts if rr else []),
        options_flow=options_res.data,
        freshness=build_freshness_report(bundle_time, fetched_at_by_source, policy),
    )

    out_json = json.dumps(bundle.model_dump(mode="json"), indent=2)
    if args.out == "-":
        print(out_json)
    else:
        with open(args.out, "w", encoding="utf-8") as file:
            file.write(out_json)


if __name__ == "__main__":
    main()
