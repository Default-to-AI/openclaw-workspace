from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from axe_core import Tracer
from axe_core.paths import project_root, public_dir

from axe_decision.openai_chat import chat_json

MODEL_DECISION = "gpt-4o"
MODEL_FAST = "gpt-4o-mini"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write_json(path: Path, data: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(obj, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _load_context(ticker: str) -> dict:
    pub = public_dir()
    ctx = {
        "ticker": ticker.upper(),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "investor_profile": _read_text(project_root() / "INVESTOR_PROFILE.md"),
        "portfolio": _read_json(pub / "portfolio.json"),
        "alpha_latest": _read_json(pub / "alpha-latest.json") if (pub / "alpha-latest.json").exists() else None,
        "news_latest": _read_json(pub / "news-latest.json") if (pub / "news-latest.json").exists() else None,
    }
    return ctx


SYSTEM_BULL = """You are Axe Capital's Bull researcher. You must build the strongest possible BUY case.
Return JSON only with keys: thesis, catalysts, valuation, technicals, risks_acknowledged, confidence_1_to_10, sources_used.
No invented facts. If data missing, say so explicitly."""

SYSTEM_BEAR = """You are Axe Capital's Bear researcher. You must build the strongest possible PASS/SELL case.
Return JSON only with keys: thesis, kill_shots, downside_scenarios, invalidation_levels, risks, confidence_1_to_10, sources_used.
No invented facts. If data missing, say so explicitly."""

SYSTEM_CRO = """You are the CRO (risk officer). Enforce hard rules: no leverage, no margin, every entry must have stop, max 20% position size, liquidity sanity.
Return JSON only with keys: gate (APPROVED|CONDITIONAL|BLOCKED), reasons, required_conditions, suggested_stop_loss_pct, suggested_position_size_pct."""

SYSTEM_CEO = """You are the CEO decision synthesizer. Use INVESTOR_PROFILE.md constraints and the provided bull/bear/CRO.
Return JSON only with keys: action (BUY|SELL|HOLD|PASS), conviction_1_to_10, thesis, entry_zone, profit_target, stop_loss, position_size_pct, bear_case, rationale, data_gaps."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="axe-decision")
    parser.add_argument("ticker", help="Ticker symbol, e.g. MSFT")
    args = parser.parse_args(argv)

    load_dotenv(project_root() / ".env", override=False)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set")

    tracer = Tracer(agent="axe_decision")
    tracer.start()

    ticker = args.ticker.upper()
    tracer.event(step="load_context", thought=f"loading context for {ticker}")
    ctx = _load_context(ticker)

    tracer.event(step="bull", thought="draft bull case")
    bull = chat_json(api_key=api_key, model=MODEL_FAST, system=SYSTEM_BULL, user=ctx, max_tokens=900)

    tracer.event(step="bear", thought="draft bear case")
    bear = chat_json(api_key=api_key, model=MODEL_FAST, system=SYSTEM_BEAR, user=ctx, max_tokens=900)

    tracer.event(step="cro", thought="risk gate")
    cro = chat_json(api_key=api_key, model=MODEL_FAST, system=SYSTEM_CRO, user={"context": ctx, "bull": bull, "bear": bear})

    tracer.event(step="ceo", thought="final decision memo")
    ceo = chat_json(api_key=api_key, model=MODEL_DECISION, system=SYSTEM_CEO, user={"context": ctx, "bull": bull, "bear": bear, "cro": cro})

    pub = public_dir()
    pub.mkdir(parents=True, exist_ok=True)

    artifact = {
        "generated_at": ctx["generated_at"],
        "ticker": ticker,
        "bull": bull,
        "bear": bear,
        "cro": cro,
        "ceo": ceo,
    }

    latest_path = pub / "decision-latest.json"
    _atomic_write_json(latest_path, artifact)

    archive_dir = pub / "decisions"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{ticker}-{ctx['generated_at'].replace(':','-')}.json"
    _atomic_write_json(archive_path, artifact)

    log_path = pub / "decision-log.jsonl"
    _append_jsonl(
        log_path,
        {
            "ts": ctx["generated_at"],
            "decision_type": "decision_memo",
            "ticker": ticker,
            "action": ceo.get("action"),
            "summary": ceo.get("thesis", "")[:220],
            "run_id": tracer.run_id,
            "tags": ["step3", "memo"],
        },
    )

    tracer.finalize(status="success", summary=f"decision memo generated for {ticker}", artifact_written="decision-latest.json")
    print(json.dumps({"latest": str(latest_path), "archive": str(archive_path), "run_id": tracer.run_id}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
