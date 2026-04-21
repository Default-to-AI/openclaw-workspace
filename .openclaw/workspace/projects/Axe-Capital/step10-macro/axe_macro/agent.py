from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import yfinance
from axe_core import Tracer
from axe_core.llm import chat_json
from axe_core.paths import public_dir
from axe_fundamental.reports import update_report_index


SYSTEM_PROMPT = """You are Axe Capital's Macro Strategist. Analyze rates, USD,
liquidity, market regime, sector rotation, and how macro conditions affect this holding.
Return JSON only with keys: summary, key_findings, data_sources, confidence, report, metrics."""


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _file_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _confidence_score(value: Any) -> int:
    numeric = _safe_float(value)
    if numeric is not None:
        return max(1, min(10, int(round(numeric))))

    label = str(value or "").strip().lower()
    label_scores = {
        "very high": 9,
        "high": 8,
        "medium": 5,
        "moderate": 5,
        "low": 3,
        "very low": 2,
    }
    return label_scores.get(label, 5)


def infer_asset_context(info: dict[str, Any]) -> dict[str, Any]:
    quote_type = str(info.get("quoteType") or info.get("typeDisp") or "UNKNOWN").upper()
    category = str(info.get("category") or "").strip()
    sector = str(info.get("sector") or "").strip()
    industry = str(info.get("industry") or "").strip()
    instrument_type = "ETF" if "ETF" in quote_type else quote_type

    exposures: list[str] = []
    for value in (category, sector, industry):
        if value and value not in exposures:
            exposures.append(value)

    return {
        "instrument_type": instrument_type,
        "macro_exposures": exposures,
    }


def normalize_macro_context(ticker: str, info: dict[str, Any]) -> dict[str, Any]:
    asset_context = infer_asset_context(info)
    return {
        "ticker": ticker.upper(),
        "instrument_type": asset_context["instrument_type"],
        "sector": info.get("sector") or info.get("category") or "Unknown",
        "industry": info.get("industry") or "Unknown",
        "country": info.get("country") or "Unknown",
        "currency": info.get("currency") or "Unknown",
        "market_cap": info.get("marketCap"),
        "beta": info.get("beta"),
        "macro_exposures": asset_context["macro_exposures"],
    }


def _normalize_result(ticker: str, context: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": _utc_stamp(),
        "ticker": ticker.upper(),
        "agent": "macro",
        "summary": str(result.get("summary") or "Macro analysis completed with limited source data."),
        "key_findings": list(result.get("key_findings") or []),
        "data_sources": list(result.get("data_sources") or ["yfinance"]),
        "confidence": _confidence_score(result.get("confidence")),
        "report": result.get("report") or "",
        "metrics": result.get("metrics") or context,
    }


def _markdown(report: dict[str, Any]) -> str:
    findings = "\n".join(f"- {item}" for item in report.get("key_findings", [])) or "- No key findings returned."
    metrics = "\n".join(f"- **{key}:** {value}" for key, value in report.get("metrics", {}).items())
    return f"""# Macro Analysis: {report["ticker"]}

**Date:** {report["generated_at"]}
**Analyst:** Macro Strategist
**Confidence:** {report["confidence"]}/10

---

## Executive Summary

{report["summary"]}

## Key Findings

{findings}

## Macro Context

{metrics}

## Detailed Report

{report["report"]}

## Data Sources

{", ".join(report.get("data_sources", []))}
"""


def run_macro_analysis(ticker: str, api_key: str, force: bool = False) -> dict:
    symbol = ticker.upper()
    tracer = Tracer(agent="axe_macro")
    tracer.start()

    reports_dir = public_dir() / "analyst-reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = _file_stamp()
    json_path = reports_dir / f"{symbol}-macro-{stamp}.json"
    md_path = reports_dir / f"{symbol}-macro-{stamp}.md"

    tracer.event(step="fetch_data", thought=f"fetching macro context for {symbol}")
    info = yfinance.Ticker(symbol).info
    context = normalize_macro_context(symbol, info)

    tracer.event(step="llm_analysis", thought="running macro strategy analysis")
    result = chat_json(api_key=api_key, model="gpt-4o-mini", system=SYSTEM_PROMPT, user=context)
    report = _normalize_result(symbol, context, result)

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    update_report_index(reports_dir, symbol, "macro", json_path, md_path)

    tracer.finalize(status="success", summary=f"macro report generated for {symbol}", artifact_written=json_path.name)
    return {"json_path": json_path, "md_path": md_path, "skipped": False}
