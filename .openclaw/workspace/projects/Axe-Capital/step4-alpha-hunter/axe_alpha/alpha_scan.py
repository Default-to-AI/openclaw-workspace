from __future__ import annotations

import asyncio
import inspect
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx
import yfinance as yf

from axe_alpha.util import project_root, workspace_root


def _safe_float(value: Any) -> float | None:
    """Canonical float coercion — matches axe_coo/util/numbers.py safe_float."""
    try:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = (
                value.strip()
                .replace(",", "")
                .replace("$", "")
                .replace("%", "")
                .replace("\u2212", "-")
            )
            if cleaned.startswith("+"):
                cleaned = cleaned[1:]
            if not cleaned:
                return None
            return float(cleaned)
        return float(value)
    except Exception:
        return None

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
LLM_MODEL = "gpt-4o-mini"
_sec_contact = os.getenv("SEC_CONTACT_EMAIL", "contact@axe-alpha-hunter.invalid")
SEC_UA = f"AxeCapitalAlphaHunter/0.1 (research; contact: {_sec_contact})"
MEGA_CAP_TECH = {"AAPL", "MSFT", "GOOG", "GOOGL", "META", "AMZN", "NVDA", "TSLA", "QQQ", "ASML"}


@dataclass
class Candidate:
    ticker: str
    opportunity_type: str
    trigger_source: str
    trigger_data_point: str
    raw_facts: dict[str, Any]
    detected_at: str
    base_score: float


def _headers() -> dict[str, str]:
    return {"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"}


def _load_investor_profile() -> str:
    return (project_root().parent / "INVESTOR_PROFILE.md").read_text(encoding="utf-8")


def _held_symbols(profile_text: str) -> set[str]:
    symbols: set[str] = set()
    in_table = False
    for line in profile_text.splitlines():
        if line.strip() == "### IBKR Holdings — Current Positions":
            in_table = True
            continue
        if in_table and line.startswith("**IBKR NAV**"):
            break
        if in_table and line.strip().startswith("|"):
            parts = [x.strip() for x in line.strip().strip("|").split("|")]
            if parts and parts[0] not in {"Symbol", "---", "Cash", ""}:
                symbols.add(parts[0])
    return symbols


def _profile_filter_blocked(ticker: str) -> bool:
    return ticker.upper() in MEGA_CAP_TECH


def _recent_business_days(days: int = 5) -> list[datetime]:
    now = datetime.now(ZoneInfo("Asia/Jerusalem"))
    out = []
    cursor = now
    while len(out) < days:
        if cursor.weekday() < 5:
            out.append(cursor)
        cursor -= timedelta(days=1)
    return out


def fetch_recent_8k_events(limit: int = 120) -> list[Candidate]:
    url = "https://www.sec.gov/files/company_tickers.json"
    with httpx.Client(timeout=20.0, headers=_headers()) as client:
        ticker_map = client.get(url).json()
        feed = client.get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&owner=include&count=100&output=atom").text

    entries = re.findall(r"<entry>(.*?)</entry>", feed, re.DOTALL)
    candidates: list[Candidate] = []
    event_patterns = [
        ("asset sale", r"asset sale|sale of .*asset|divest"),
        ("leadership change", r"appoint|resign|chief executive|chief financial|director"),
        ("contract award", r"contract|award|agreement|order"),
        ("restructuring", r"restructur|spin-?off|separation|strategic alternatives"),
    ]

    ticker_lookup = {str(v.get('cik_str')).zfill(10): str(v.get('ticker', '')).upper() for v in ticker_map.values()}

    for entry in entries[:limit]:
        title = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
        summary = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
        updated = re.search(r"<updated>(.*?)</updated>", entry)
        link = re.search(r'<link href="(.*?)"', entry)
        category = None
        hay = f"{title.group(1) if title else ''} {summary.group(1) if summary else ''}".lower()
        for name, pattern in event_patterns:
            if re.search(pattern, hay):
                category = name
                break
        if not category:
            continue
        cik_match = re.search(r"CIK=(\d+)", link.group(1) if link else "")
        ticker = ticker_lookup.get(str(cik_match.group(1)).zfill(10)) if cik_match else None
        if not ticker:
            continue
        candidates.append(Candidate(
            ticker=ticker,
            opportunity_type="8k_event",
            trigger_source="sec_edgar",
            trigger_data_point=category,
            raw_facts={
                "title": re.sub(r"<.*?>", "", title.group(1) if title else ""),
                "summary": re.sub(r"<.*?>", "", summary.group(1) if summary else ""),
                "filing_url": link.group(1) if link else None,
            },
            detected_at=updated.group(1) if updated else datetime.now(UTC).isoformat(),
            base_score=6.4 if category != "restructuring" else 7.0,
        ))
    return candidates


def fetch_recent_form4_candidates(limit_companies: int = 180) -> list[Candidate]:
    url = "https://www.sec.gov/files/company_tickers.json"
    with httpx.Client(timeout=20.0, headers=_headers()) as client:
        ticker_map = client.get(url).json()
    companies = list(ticker_map.values())[:limit_companies]
    candidates: list[Candidate] = []
    cutoff = datetime.now(UTC) - timedelta(days=30)

    with httpx.Client(timeout=15.0, headers=_headers()) as client:
        for row in companies:
            ticker = str(row.get("ticker", "")).upper()
            cik = str(row.get("cik_str", "")).zfill(10)
            try:
                data = client.get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()
            except Exception:
                continue
            recent = ((data.get("filings") or {}).get("recent") or {})
            forms = recent.get("form") or []
            dates = recent.get("filingDate") or []
            accessions = recent.get("accessionNumber") or []
            primary_docs = recent.get("primaryDocument") or []
            form4_hits = []
            total_buy_value = 0.0
            buyers = 0
            for idx, form in enumerate(forms[:20]):
                if form != "4":
                    continue
                filed = dates[idx] if idx < len(dates) else None
                if not filed:
                    continue
                try:
                    filed_dt = datetime.fromisoformat(filed).replace(tzinfo=UTC)
                except Exception:
                    continue
                if filed_dt < cutoff:
                    continue
                accession = (accessions[idx] if idx < len(accessions) else "").replace("-", "")
                primary = primary_docs[idx] if idx < len(primary_docs) else ""
                if not accession or not primary:
                    continue
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary}"
                try:
                    xml = client.get(filing_url).text
                except Exception:
                    continue
                trans_codes = re.findall(r"<transactionCode>(.*?)</transactionCode>", xml)
                if "P" not in trans_codes:
                    continue
                shares_vals = [_safe_float(x) or 0.0 for x in re.findall(r"<transactionShares>.*?<value>(.*?)</value>.*?</transactionShares>", xml, re.DOTALL)]
                price_vals = [_safe_float(x) or 0.0 for x in re.findall(r"<transactionPricePerShare>.*?<value>(.*?)</value>.*?</transactionPricePerShare>", xml, re.DOTALL)]
                owner_match = re.search(r"<rptOwnerName>(.*?)</rptOwnerName>", xml)
                owner = owner_match.group(1).strip() if owner_match else f"insider_{idx}"
                buy_value = 0.0
                for shares, price in zip(shares_vals, price_vals):
                    buy_value += shares * price
                if buy_value <= 0:
                    continue
                buyers += 1
                total_buy_value += buy_value
                form4_hits.append({"owner": owner, "buy_value": round(buy_value, 2), "filing_url": filing_url, "filed": filed})
            if buyers >= 3 or total_buy_value >= 500_000:
                candidates.append(Candidate(
                    ticker=ticker,
                    opportunity_type="insider_buy",
                    trigger_source="sec_form4",
                    trigger_data_point=f"{buyers} insider buys totaling ${total_buy_value:,.0f} in last 30d",
                    raw_facts={"buyers": buyers, "total_buy_value": round(total_buy_value, 2), "filings": form4_hits[:5]},
                    detected_at=datetime.now(UTC).isoformat(),
                    base_score=7.4 if total_buy_value >= 1_000_000 else 6.8,
                ))
            time.sleep(0.11)  # ~9 req/s — stay within SEC's 10 req/s guidance
    return candidates


def fetch_earnings_drift_candidates(tickers: list[str]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            earnings_dates = t.earnings_dates
            if earnings_dates is None or len(earnings_dates) == 0:
                continue
            last_idx = earnings_dates.index[0].to_pydatetime()
            if datetime.now(last_idx.tzinfo or UTC) - last_idx > timedelta(days=14):
                continue
            hist = t.history(period="1mo", interval="1d", auto_adjust=False)
            if hist is None or len(hist) < 6:
                continue
            close_before = float(hist.iloc[-6]["Close"])
            close_after = float(hist.iloc[-1]["Close"])
            reaction_pct = ((close_after / close_before) - 1) * 100 if close_before else 0.0
            info = t.get_info() or {}
            eps_current = _safe_float(info.get("trailingEps"))
            eps_forward = _safe_float(info.get("forwardEps"))
            if eps_current is None or eps_forward is None or eps_forward <= eps_current:
                continue
            if abs(reaction_pct) > 4.0:
                continue
            candidates.append(Candidate(
                ticker=ticker,
                opportunity_type="earnings_drift",
                trigger_source="yfinance_earnings",
                trigger_data_point=f"Forward EPS {eps_forward:.2f} vs trailing {eps_current:.2f}, price reaction only {reaction_pct:.2f}%",
                raw_facts={"reaction_pct": round(reaction_pct, 2), "trailing_eps": eps_current, "forward_eps": eps_forward, "last_earnings_date": last_idx.date().isoformat()},
                detected_at=datetime.now(UTC).isoformat(),
                base_score=6.9,
            ))
        except Exception:
            continue
    return candidates


def fetch_spinoff_restructuring_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []
    ddg_module_path = workspace_root() / "skills" / "stock-market-pro" / "scripts"
    if str(ddg_module_path) not in __import__("sys").path:
        __import__("sys").path.append(str(ddg_module_path))
    try:
        import ddg_search  # type: ignore
    except Exception:
        return candidates
    queries = [
        "site:sec.gov spin-off company no analyst coverage stock",
        "site:sec.gov restructuring strategic alternatives small cap stock",
    ]
    for query in queries:
        try:
            results = ddg_search.search_text(query, max_results=8)
        except Exception:
            continue
        for item in results[:5]:
            title = str(item.get("title", ""))
            body = str(item.get("body", ""))
            text = f"{title} {body}"
            ticker_match = re.search(r"\(([A-Z]{1,5})\)", text)
            if not ticker_match:
                ticker_match = re.search(r"\b([A-Z]{2,5})\b", text)
            ticker = ticker_match.group(1) if ticker_match else None
            if not ticker or ticker in {"SEC", "FORM", "CEO", "ETF"}:
                continue
            candidates.append(Candidate(
                ticker=ticker,
                opportunity_type="spinoff",
                trigger_source="ddg_sec_search",
                trigger_data_point=title[:180],
                raw_facts={"title": title, "body": body, "url": item.get("href")},
                detected_at=datetime.now(UTC).isoformat(),
                base_score=6.7,
            ))
    return candidates


async def fetch_options_flow_candidates(tickers: list[str]) -> list[Candidate]:
    candidates: list[Candidate] = []
    vendor_dir = project_root().parent / "step1-data-foundation"
    if str(vendor_dir) not in sys.path:
        sys.path.append(str(vendor_dir))
    try:
        from axe_coo.vendors import uw as uw_vendor  # type: ignore
    except Exception:
        return candidates
    free_flow_tickers = [t for t in tickers if t in {"JPM", "INTC", "IWM", "XSP"}]
    for ticker in free_flow_tickers:
        try:
            coro = uw_vendor._run_with_timeout(ticker, total_timeout_s=20)
            if not inspect.isawaitable(coro):
                continue
            data = await coro
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        flow = data.get("flow") or []
        overview = data.get("overview") or {}
        whales = [row for row in flow if (_safe_float(row.get("premium")) or 0) >= 100_000]
        unusual = [row for row in flow if row.get("vol_gt_oi")]
        pc_ratio = overview.get("pc_ratio")
        if not whales and not unusual:
            continue
        candidates.append(Candidate(
            ticker=ticker,
            opportunity_type="options_flow",
            trigger_source="unusual_whales",
            trigger_data_point=f"{len(whales)} whale trades, {len(unusual)} vol>OI trades, put/call ratio {pc_ratio}",
            raw_facts={"overview": overview, "whales": whales[:5], "unusual_entries": unusual[:5]},
            detected_at=datetime.now(UTC).isoformat(),
            base_score=7.2 if whales else 6.5,
        ))
    return candidates


async def _llm_summarize_candidate(client: httpx.AsyncClient, api_key: str, candidate: Candidate, profile_guardrail: str) -> dict[str, Any]:
    payload = {
        "model": LLM_MODEL,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Axe Capital's Alpha Hunter summarizer. Read INVESTOR_PROFILE.md before every decision. "
                    "Return JSON only. Do not invent facts. Summarize the already-identified opportunity into: "
                    "ticker, opportunity_type, thesis_one_line, conviction_1_to_10, why_retail_is_missing_this, risk_flags."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "profile_guardrail": profile_guardrail,
                    "candidate": {
                        "ticker": candidate.ticker,
                        "opportunity_type": candidate.opportunity_type,
                        "trigger_source": candidate.trigger_source,
                        "trigger_data_point": candidate.trigger_data_point,
                        "raw_facts": candidate.raw_facts,
                        "base_score": candidate.base_score,
                    },
                }, ensure_ascii=False),
            },
        ],
    }
    response = await client.post(
        OPENAI_CHAT_COMPLETIONS_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
    )
    response.raise_for_status()
    return json.loads(response.json()["choices"][0]["message"]["content"])


def _dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    best: dict[tuple[str, str], Candidate] = {}
    for candidate in candidates:
        key = (candidate.ticker, candidate.opportunity_type)
        current = best.get(key)
        if current is None or candidate.base_score > current.base_score:
            best[key] = candidate
    return list(best.values())


def _rank_key(item: dict[str, Any]) -> tuple[float, float]:
    return (_safe_float(item.get("conviction_score")) or 0.0, _safe_float(item.get("base_score")) or 0.0)


async def run_alpha_hunter_scan(api_key: str) -> dict[str, Any]:
    profile_text = _load_investor_profile()
    held = _held_symbols(profile_text)
    profile_guardrail = (
        "Filter out opportunities that add to Robert's existing US large cap tech concentration unless conviction is 9+. "
        f"Currently held symbols include: {sorted(held)}"
    )

    scan_universe = [
        "JPM", "INTC", "IWM", "XSP", "CVX", "XOM", "PFE", "JNJ", "RTX", "BA",
        "UNH", "MRK", "CAT", "DE", "GE", "MMM", "SLB", "COP", "NEM", "OXY",
        "WBA", "CAG", "KHC", "GIS", "ADM", "LUV", "DAL", "UAL", "ET", "KMI",
    ]

    candidates = []
    candidates.extend(fetch_recent_8k_events())
    candidates.extend(fetch_recent_form4_candidates())
    candidates.extend(fetch_earnings_drift_candidates(scan_universe))
    candidates.extend(fetch_spinoff_restructuring_candidates())
    candidates.extend(await fetch_options_flow_candidates(scan_universe))
    deduped = _dedupe_candidates(candidates)
    deduped.sort(key=lambda c: c.base_score, reverse=True)
    deduped = deduped[:12]

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        summaries = await asyncio.gather(*[
            _llm_summarize_candidate(client, api_key, candidate, profile_guardrail)
            for candidate in deduped
        ])

    ranked = []
    for candidate, summary in zip(deduped, summaries):
        conviction = int(round(_safe_float(summary.get("conviction_1_to_10")) or candidate.base_score))
        if _profile_filter_blocked(candidate.ticker) and conviction < 9:
            continue
        ranked.append({
            "ticker": candidate.ticker,
            "opportunity_type": candidate.opportunity_type,
            "thesis": summary.get("thesis_one_line"),
            "conviction_score": conviction,
            "trigger_source": candidate.trigger_source,
            "trigger_data_point": candidate.trigger_data_point,
            "why_retail_is_missing_this": summary.get("why_retail_is_missing_this"),
            "risk_flags": summary.get("risk_flags") or [],
            "detected_at": candidate.detected_at,
            "raw_facts": candidate.raw_facts,
            "base_score": round(candidate.base_score, 2),
        })

    ranked.sort(key=_rank_key, reverse=True)
    top5 = ranked[:5]
    now_local = datetime.now(ZoneInfo("Asia/Jerusalem"))
    report = {
        "report_date": now_local.date().isoformat(),
        "generated_at": now_local.isoformat(),
        "model_for_summaries": LLM_MODEL,
        "scan_logic": "pure_python",
        "investor_profile_guardrail": profile_guardrail,
        "opportunity_count_before_filter": len(candidates),
        "opportunity_count_after_filter": len(ranked),
        "top_opportunities": top5,
    }
    return report


def report_path_for_date(report_date: str) -> Path:
    return project_root() / "reports" / f"{report_date}.json"
