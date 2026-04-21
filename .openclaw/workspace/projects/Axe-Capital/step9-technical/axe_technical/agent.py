from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yfinance
from axe_core import Tracer
from axe_core.llm import chat_json
from axe_core.paths import public_dir
from axe_fundamental.reports import update_report_index


SYSTEM_PROMPT = """You are Axe Capital's Technical Analyst. Analyze trend, market structure,
support, resistance, invalidation, entry/exit framing, and volume confirmation.
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


def classify_trend(last_price: float | None, sma_50: float | None, sma_200: float | None) -> str:
    if last_price is None or sma_50 is None or sma_200 is None:
        return "unknown"
    if last_price > sma_50 > sma_200:
        return "uptrend"
    if last_price < sma_50 < sma_200:
        return "downtrend"
    return "mixed"


def _rows_from_history(history: Any) -> list[dict[str, Any]]:
    if hasattr(history, "reset_index"):
        return history.reset_index().to_dict("records")
    return list(history or [])


def _average(values: Iterable[float]) -> float | None:
    vals = [value for value in values if value is not None]
    if not vals:
        return None
    return round(sum(vals) / len(vals), 4)


def build_technical_context(ticker: str, history: Any) -> dict[str, Any]:
    rows = _rows_from_history(history)
    closes = [_safe_float(row.get("Close")) for row in rows]
    highs = [_safe_float(row.get("High")) for row in rows]
    lows = [_safe_float(row.get("Low")) for row in rows]
    volumes = [_safe_float(row.get("Volume")) for row in rows]

    close_vals = [value for value in closes if value is not None]
    high_vals = [value for value in highs if value is not None]
    low_vals = [value for value in lows if value is not None]
    volume_vals = [value for value in volumes if value is not None]

    last_price = close_vals[-1] if close_vals else None
    sma_20 = _average(close_vals[-20:])
    sma_50 = _average(close_vals[-50:])
    sma_200 = _average(close_vals[-200:])
    support = round(min(low_vals[-60:] or low_vals), 4) if low_vals else None
    resistance = round(max(high_vals[-60:] or high_vals), 4) if high_vals else None

    return {
        "ticker": ticker.upper(),
        "last_price": last_price,
        "sma_20": sma_20,
        "sma_50": sma_50,
        "sma_200": sma_200,
        "support": support,
        "resistance": resistance,
        "trend": classify_trend(last_price, sma_50, sma_200),
        "average_volume_20d": _average(volume_vals[-20:]),
        "observations": len(rows),
    }


def _normalize_result(ticker: str, context: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": _utc_stamp(),
        "ticker": ticker.upper(),
        "agent": "technical",
        "summary": str(result.get("summary") or "Technical analysis completed with limited source data."),
        "key_findings": list(result.get("key_findings") or []),
        "data_sources": list(result.get("data_sources") or ["yfinance"]),
        "confidence": _confidence_score(result.get("confidence")),
        "report": result.get("report") or "",
        "metrics": result.get("metrics") or context,
    }


def _markdown(report: dict[str, Any]) -> str:
    findings = "\n".join(f"- {item}" for item in report.get("key_findings", [])) or "- No key findings returned."
    metrics = "\n".join(f"- **{key}:** {value}" for key, value in report.get("metrics", {}).items())
    return f"""# Technical Analysis: {report["ticker"]}

**Date:** {report["generated_at"]}
**Analyst:** Technical Agent
**Confidence:** {report["confidence"]}/10

---

## Executive Summary

{report["summary"]}

## Key Findings

{findings}

## Technical Metrics

{metrics}

## Detailed Report

{report["report"]}

## Data Sources

{", ".join(report.get("data_sources", []))}
"""


def run_technical_analysis(ticker: str, api_key: str, force: bool = False) -> dict:
    symbol = ticker.upper()
    tracer = Tracer(agent="axe_technical")
    tracer.start()

    reports_dir = public_dir() / "analyst-reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = _file_stamp()
    json_path = reports_dir / f"{symbol}-technical-{stamp}.json"
    md_path = reports_dir / f"{symbol}-technical-{stamp}.md"

    tracer.event(step="fetch_data", thought=f"fetching price history for {symbol}")
    history = yfinance.Ticker(symbol).history(period="1y", interval="1d")
    context = build_technical_context(symbol, history)

    tracer.event(step="llm_analysis", thought="running technical analysis")
    result = chat_json(api_key=api_key, model="gpt-4o-mini", system=SYSTEM_PROMPT, user=context)
    report = _normalize_result(symbol, context, result)

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    update_report_index(reports_dir, symbol, "technical", json_path, md_path)

    tracer.finalize(status="success", summary=f"technical report generated for {symbol}", artifact_written=json_path.name)
    return {"json_path": json_path, "md_path": md_path, "skipped": False}
