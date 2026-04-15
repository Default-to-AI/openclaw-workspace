"""LLM-based impact scoring using OpenAI (JSON-only)"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

import httpx

from axe_news.ingest import RawItem

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o-mini"
MODEL_NAME_FOR_ARTIFACT = "gpt-4o-mini"

PortfolioRelevance = Literal["held", "watchlist", "sector", "none"]

SYSTEM_PROMPT = """You are the impact analyst for Axe Capital, a small personal-investment research shop.

Your job: given one news item, return ONE JSON object scoring whether this item should reach a human investor. No prose outside the JSON.

Schema:
{
  "impact_score": <int 0..10>,
  "impact_rationale": "<1 sentence on why this moves markets or changes a decision>",
  "decision_hook": "<1 sentence action hint OR null>",
  "portfolio_relevance": "held" | "watchlist" | "sector" | "none"
}

Scoring rubric (anchor to 6):
  9-10: Highly likely to change a portfolio decision today (regulatory action on a held name, tender/M&A bid, major guide cut).
  7-8:  Significant strategic shift (regulatory probe opened, exec departure, macro regime change, real supply-chain disruption).
  6:    Credible event worth surfacing; reader should be aware before next decision.
  <=5:  Do not surface. Score below 6 means rejection.

HARD REJECT rules (always score <=5):
- Analyst rating changes
- Price-target changes of any direction
- Routine earnings-preview speculation without hard data
- Generic market commentary / sector recap / "what to watch"
- Conference/event reminders
- Already-reported news with no new info

HARD KEEP rules (lean 7+ unless info is thin):
- Regulatory actions, investigations, enforcement
- M&A announcements, tender offers, rumored bids with sourced detail
- Major product/strategy shifts, platform changes, pricing model changes
- C-suite departures, founder changes, board shake-ups
- Macro/geopolitical events that reshape sector dynamics (rate shocks, export controls)
- Concrete litigation milestones
- Supply-chain disruptions affecting known suppliers/customers of watchlist names

Default to skepticism: if uncertain between 5 and 6, choose 5.
"""


@dataclass
class ImpactScore:
    impact_score: int
    impact_rationale: str
    decision_hook: str | None
    portfolio_relevance: PortfolioRelevance


def build_prompt(item: RawItem, tickers: list[str]) -> str:
    return (
        f"Tickers in watchlist mentioned: {', '.join(tickers) if tickers else '(none)'}\n"
        f"Source: {item.source}\n"
        f"Published: {item.published_at}\n"
        f"Title: {item.title}\n"
        f"Summary: {item.summary}\n"
        f"URL: {item.url}\n\n"
        f"Return the JSON object only."
    )


_FENCE_RE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL)


def parse_response(text: str) -> ImpactScore | None:
    match = _FENCE_RE.search(text)
    payload = match.group(1) if match else text
    try:
        data = json.loads(payload)
        return ImpactScore(
            impact_score=int(data["impact_score"]),
            impact_rationale=str(data["impact_rationale"]),
            decision_hook=data.get("decision_hook"),
            portfolio_relevance=data["portfolio_relevance"],
        )
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def score_item(
    item: RawItem,
    tickers: list[str],
    relevance: PortfolioRelevance,
    api_key: str,
) -> ImpactScore | None:
    payload = {
        "model": MODEL,
        "temperature": 0.2,
        "max_tokens": 400,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(item, tickers)},
        ],
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            OPENAI_CHAT_COMPLETIONS_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
    result = parse_response(text)
    if result and result.portfolio_relevance not in ("held", "watchlist", "sector", "none"):
        # Normalize bad enum back to "none".
        result = ImpactScore(
            impact_score=result.impact_score,
            impact_rationale=result.impact_rationale,
            decision_hook=result.decision_hook,
            portfolio_relevance="none",
        )
    return result
