from __future__ import annotations

import asyncio
import json
import math
import time
from dataclasses import dataclass
from statistics import mean
from typing import Any

import httpx

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4.1-mini"


@dataclass(frozen=True)
class AnalystSpec:
    name: str
    role: str
    output_keys: list[str]
    focus_builder: callable
    system_prompt: str
    model: str = DEFAULT_MODEL


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _round(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def _latest_close(prices: list[dict[str, Any]]) -> float | None:
    if not prices:
        return None
    return _safe_float(prices[-1].get("close"))


def _compute_technical_snapshot(prices: list[dict[str, Any]]) -> dict[str, Any]:
    closes = [_safe_float(row.get("close")) for row in prices]
    closes = [x for x in closes if x is not None]
    volumes = [_safe_float(row.get("volume")) for row in prices]
    volumes = [x for x in volumes if x is not None]

    latest_close = closes[-1] if closes else None
    sma_20 = mean(closes[-20:]) if len(closes) >= 20 else None
    sma_50 = mean(closes[-50:]) if len(closes) >= 50 else None

    def rsi_14(vals: list[float]) -> float | None:
        if len(vals) < 15:
            return None
        deltas = [vals[i] - vals[i - 1] for i in range(1, len(vals))]
        gains = [max(delta, 0) for delta in deltas[-14:]]
        losses = [abs(min(delta, 0)) for delta in deltas[-14:]]
        avg_gain = mean(gains) if gains else 0
        avg_loss = mean(losses) if losses else 0
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    returns = []
    for idx in range(1, len(closes)):
        prev = closes[idx - 1]
        curr = closes[idx]
        if prev:
            returns.append((curr - prev) / prev)

    support = min(closes[-20:]) if len(closes) >= 20 else (min(closes) if closes else None)
    resistance = max(closes[-20:]) if len(closes) >= 20 else (max(closes) if closes else None)

    return {
        "latest_close": _round(latest_close, 4),
        "sma_20": _round(sma_20, 4),
        "sma_50": _round(sma_50, 4),
        "rsi_14": _round(rsi_14(closes), 2),
        "return_5d_pct": _round(((closes[-1] / closes[-6]) - 1) * 100, 2) if len(closes) >= 6 else None,
        "return_20d_pct": _round(((closes[-1] / closes[-21]) - 1) * 100, 2) if len(closes) >= 21 else None,
        "avg_volume_20d": _round(mean(volumes[-20:]), 2) if len(volumes) >= 20 else None,
        "support_20d": _round(support, 4),
        "resistance_20d": _round(resistance, 4),
        "price_rows_used": len(prices[-90:]),
    }


def _latest_macro_points(bundle: dict[str, Any]) -> dict[str, Any]:
    macro = bundle.get("macro") or {}
    latest: dict[str, Any] = {}
    for series_id, points in macro.items():
        if points:
            latest[series_id] = points[0]
    return latest


def _source_status(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "name": src.get("name"),
            "ok": src.get("ok"),
            "stale": src.get("stale"),
            "error": src.get("error"),
            "meta": src.get("meta"),
        }
        for src in (bundle.get("sources") or [])
    ]


def _fundamental_context(bundle: dict[str, Any]) -> dict[str, Any]:
    prices = ((bundle.get("prices") or {}).get("rows") or [])
    return {
        "ticker": bundle.get("ticker"),
        "fetched_at": bundle.get("fetched_at"),
        "sources": _source_status(bundle),
        "financial_snapshot": bundle.get("financial_snapshot"),
        "earnings_dates": bundle.get("earnings_dates"),
        "recent_sec_filings": (bundle.get("sec_filings") or [])[:15],
        "recent_news": (bundle.get("news") or [])[:8],
        "price_summary": {
            "latest_close": _latest_close(prices),
            "technical_snapshot": _compute_technical_snapshot(prices),
        },
    }


def _technical_context(bundle: dict[str, Any]) -> dict[str, Any]:
    prices = ((bundle.get("prices") or {}).get("rows") or [])
    return {
        "ticker": bundle.get("ticker"),
        "fetched_at": bundle.get("fetched_at"),
        "sources": _source_status(bundle),
        "technical_snapshot": _compute_technical_snapshot(prices),
        "recent_prices": prices[-90:],
        "recent_news_headlines": [
            {
                "title": item.get("title"),
                "published_at": item.get("published_at"),
                "source": item.get("source"),
            }
            for item in (bundle.get("news") or [])[:6]
        ],
    }


def _sentiment_context(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": bundle.get("ticker"),
        "fetched_at": bundle.get("fetched_at"),
        "sources": _source_status(bundle),
        "news": bundle.get("news") or [],
        "reddit": bundle.get("reddit") or [],
        "options_flow": bundle.get("options_flow"),
    }


def _macro_context(bundle: dict[str, Any]) -> dict[str, Any]:
    prices = ((bundle.get("prices") or {}).get("rows") or [])
    return {
        "ticker": bundle.get("ticker"),
        "fetched_at": bundle.get("fetched_at"),
        "sources": _source_status(bundle),
        "latest_macro_points": _latest_macro_points(bundle),
        "macro_history": bundle.get("macro") or {},
        "financial_snapshot": bundle.get("financial_snapshot"),
        "price_summary": _compute_technical_snapshot(prices),
        "recent_news": (bundle.get("news") or [])[:6],
    }


ANALYST_SPECS: dict[str, AnalystSpec] = {
    "fundamental": AnalystSpec(
        name="fundamental",
        role="Fundamental Analyst",
        output_keys=[
            "ticker",
            "analyst",
            "score_1_to_10",
            "thesis",
            "key_facts",
            "valuation_view",
            "financial_strength",
            "catalysts",
            "risks",
            "confidence_1_to_10",
        ],
        focus_builder=_fundamental_context,
        system_prompt=(
            "You are Axe Capital's Fundamental Analyst. Read the COO bundle context and return a strict JSON object only. "
            "Do not use markdown. Focus on balance sheet, cash flow, profitability, valuation, filings, and earnings setup. "
            "Required keys: ticker, analyst, score_1_to_10, thesis, key_facts, valuation_view, financial_strength, catalysts, risks, confidence_1_to_10. "
            "key_facts, catalysts, risks must be arrays of concise strings. financial_strength must be an object with strengths and weaknesses arrays."
        ),
    ),
    "technical": AnalystSpec(
        name="technical",
        role="Technical Analyst",
        output_keys=[
            "ticker",
            "analyst",
            "score_1_to_10",
            "trend",
            "setup",
            "entry_zone",
            "stop_loss",
            "take_profit_zone",
            "indicators",
            "risks",
            "confidence_1_to_10",
        ],
        focus_builder=_technical_context,
        system_prompt=(
            "You are Axe Capital's Technical Analyst. Read the COO bundle context and return a strict JSON object only. "
            "Do not use markdown. Focus on trend, support/resistance, moving averages, RSI, momentum, and actionable levels. "
            "Required keys: ticker, analyst, score_1_to_10, trend, setup, entry_zone, stop_loss, take_profit_zone, indicators, risks, confidence_1_to_10. "
            "entry_zone and take_profit_zone must be objects with low and high numeric-or-null fields. stop_loss must be numeric-or-null. "
            "indicators must be an object summarizing sma_20_vs_price, sma_50_vs_price, rsi_14, momentum_20d_pct. risks must be an array of strings."
        ),
    ),
    "sentiment": AnalystSpec(
        name="sentiment",
        role="Sentiment Analyst",
        output_keys=[
            "ticker",
            "analyst",
            "score_1_to_10",
            "sentiment_bias",
            "narrative_summary",
            "top_catalysts",
            "top_risks",
            "headline_takeaways",
            "confidence_1_to_10",
        ],
        focus_builder=_sentiment_context,
        system_prompt=(
            "You are Axe Capital's Sentiment and News Analyst. Read the COO bundle context and return a strict JSON object only. "
            "Do not use markdown. Focus on news flow, narrative direction, social signal quality, and catalyst/risk asymmetry. "
            "Required keys: ticker, analyst, score_1_to_10, sentiment_bias, narrative_summary, top_catalysts, top_risks, headline_takeaways, confidence_1_to_10. "
            "top_catalysts, top_risks, headline_takeaways must be arrays of concise strings."
        ),
    ),
    "macro": AnalystSpec(
        name="macro",
        role="Macro Analyst",
        output_keys=[
            "ticker",
            "analyst",
            "score_1_to_10",
            "macro_regime",
            "tide_in_or_out",
            "macro_thesis",
            "tailwinds",
            "headwinds",
            "watch_items",
            "confidence_1_to_10",
        ],
        focus_builder=_macro_context,
        system_prompt=(
            "You are Axe Capital's Macro Analyst. Read the COO bundle context and return a strict JSON object only. "
            "Do not use markdown. Focus on rates, inflation, volatility, risk appetite, and whether the macro tide supports this ticker. "
            "Required keys: ticker, analyst, score_1_to_10, macro_regime, tide_in_or_out, macro_thesis, tailwinds, headwinds, watch_items, confidence_1_to_10. "
            "tailwinds, headwinds, watch_items must be arrays of concise strings. tide_in_or_out must be one of: in, neutral, out."
        ),
    ),
}


def _build_messages(spec: AnalystSpec, bundle: dict[str, Any]) -> list[dict[str, str]]:
    context = spec.focus_builder(bundle)
    user_prompt = (
        f"Ticker: {bundle.get('ticker')}\n"
        f"Analyst role: {spec.role}\n"
        "Use only the provided COO bundle context. If data is missing, say so inside the JSON fields rather than inventing facts.\n"
        "Return valid JSON only.\n\n"
        f"COO bundle context:\n{json.dumps(context, ensure_ascii=False)}"
    )
    return [
        {"role": "system", "content": spec.system_prompt},
        {"role": "user", "content": user_prompt},
    ]


async def _call_openai_json(
    client: httpx.AsyncClient,
    api_key: str,
    spec: AnalystSpec,
    bundle: dict[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    response = await client.post(
        OPENAI_CHAT_COMPLETIONS_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": spec.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": _build_messages(spec, bundle),
        },
    )
    response.raise_for_status()
    payload = response.json()
    message = payload["choices"][0]["message"]["content"]
    memo = json.loads(message)
    memo.setdefault("ticker", bundle.get("ticker"))
    memo.setdefault("analyst", spec.role)
    elapsed = round(time.perf_counter() - started, 3)
    return {
        "analyst": spec.name,
        "role": spec.role,
        "model": spec.model,
        "elapsed_seconds": elapsed,
        "memo": memo,
        "usage": payload.get("usage"),
    }


async def run_parallel_analysis(bundle: dict[str, Any], api_key: str, timeout_seconds: float = 120.0) -> dict[str, Any]:
    started = time.perf_counter()
    timeout = httpx.Timeout(timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [
            _call_openai_json(client, api_key, spec, bundle)
            for spec in ANALYST_SPECS.values()
        ]
        results = await asyncio.gather(*tasks)

    elapsed = round(time.perf_counter() - started, 3)
    return {
        "ticker": bundle.get("ticker"),
        "parallel": True,
        "elapsed_seconds": elapsed,
        "analyst_count": len(results),
        "results": results,
    }
