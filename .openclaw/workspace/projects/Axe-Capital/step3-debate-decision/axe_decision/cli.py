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


def _update_approval_queue(pub: Path, ticker: str, ceo: dict, generated_at: str) -> None:
    """Append actionable CEO decisions to approval-queue.md pending table."""
    action = ceo.get("action", "PASS")
    if action == "PASS":
        return  # PASS decisions don't go to the approval queue

    queue_path = pub / "approval-queue.md"
    if not queue_path.exists():
        return  # template not present, skip silently

    content = queue_path.read_text(encoding="utf-8")

    # Build the new row
    date_str = generated_at[:10]
    size = f"{ceo.get('position_size_pct', 0)}% NAV"
    thesis_short = (ceo.get("thesis") or "")[:80].replace("|", "/")
    invalidation_short = (ceo.get("stop_loss") or "")
    log_link = f"decisions/{ticker}-{generated_at.replace(':', '-')}.json"

    new_row = (
        f"| {date_str} | {ticker} | {action} | {size} "
        f"| {thesis_short} | Stop: {invalidation_short} | [{ticker} memo]({log_link}) |"
    )

    # Insert before the blank line after the table header
    marker = "| Date | Ticker | Action | Size | Thesis (1 line) | Invalidation | Decision Log |"
    header_line = "|------|--------|--------|------|-----------------|-------------|--------------|"
    if marker in content and header_line in content:
        insert_after = content.index(header_line) + len(header_line)
        content = content[:insert_after] + "\n" + new_row + content[insert_after:]
        queue_path.write_text(content, encoding="utf-8")


def _prune_decision_archive(archive_dir: Path, keep_days: int = 90) -> None:
    """Remove decision JSON files older than keep_days. Keeps decision-latest.json untouched."""
    import time
    cutoff = time.time() - (keep_days * 86400)
    for f in archive_dir.glob("*.json"):
        if f.stat().st_mtime < cutoff:
            f.unlink()


def _load_analyst_reports(ticker: str) -> dict:
    reports_dir = public_dir() / "analyst-reports"
    index_path = reports_dir / "index.json"
    if not index_path.exists():
        return {}

    try:
        index = _read_json(index_path)
    except Exception:
        return {}

    symbol_reports = index.get("symbols", {}).get(ticker.upper(), {})
    loaded: dict[str, dict] = {}
    for agent, meta in symbol_reports.items():
        json_name = meta.get("json_path") if isinstance(meta, dict) else None
        if not json_name:
            continue
        report_path = reports_dir / json_name
        if not report_path.exists():
            continue
        try:
            loaded[agent] = _read_json(report_path)
        except Exception:
            loaded[agent] = {"agent": agent, "error": f"failed to read {json_name}"}
    return loaded


def _load_context(ticker: str) -> dict:
    pub = public_dir()
    ctx = {
        "ticker": ticker.upper(),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "investor_profile": _read_text(project_root() / "INVESTOR_PROFILE.md"),
        "portfolio": _read_json(pub / "portfolio.json"),
        "alpha_latest": _read_json(pub / "alpha-latest.json") if (pub / "alpha-latest.json").exists() else None,
        "news_latest": _read_json(pub / "news-latest.json") if (pub / "news-latest.json").exists() else None,
        "analyst_reports": _load_analyst_reports(ticker),
    }
    return ctx


SYSTEM_BULL = """You are Axe Capital's Bull researcher. You must build the strongest possible BUY case.
Use analyst_reports in the context when present: fundamental, technical, and macro.
Return JSON only with keys: thesis, catalysts, valuation, technicals, risks_acknowledged, confidence_1_to_10, sources_used.
No invented facts. If data missing, say so explicitly."""

SYSTEM_BEAR = """You are Axe Capital's Bear researcher. You must build the strongest possible PASS/SELL case.
Use analyst_reports in the context when present: fundamental, technical, and macro.
Return JSON only with keys: thesis, kill_shots, downside_scenarios, invalidation_levels, risks, confidence_1_to_10, sources_used.
No invented facts. If data missing, say so explicitly."""

SYSTEM_RISK_MANAGER = """You are Axe Capital's Risk Manager. Enforce hard rules: no leverage, no margin, every entry must have a stop, max 20% position size, liquidity sanity, concentration sanity, and thesis invalidation.
Use analyst_reports in the context when present and identify any missing specialist coverage.
Return JSON only with keys: gate (APPROVED|CONDITIONAL|BLOCKED), veto_rationale, scenario_risks, required_conditions, suggested_stop_loss_pct, suggested_position_size_pct, concentration_notes."""

SYSTEM_COMPLIANCE = """You are Axe Capital's Compliance/Audit officer. You do not make the investment decision. You check whether the memo has enough evidence to be auditable.
Review context, bull, bear, and risk_manager. Return JSON only with keys: audit_status (PASS|NEEDS_MORE_EVIDENCE|FAIL), source_coverage, missing_evidence, assumption_quality, manual_approval_required, audit_notes."""

SYSTEM_CEO = """You are the CEO decision synthesizer for Axe Capital. Use INVESTOR_PROFILE.md constraints and the provided bull/bear/CRO inputs.
Use analyst_reports, risk_manager, and compliance in the context when present. If specialist reports are absent, put that in data_gaps.

Choose exactly one action from this vocabulary — pick the most precise one:
  BUY            — initiate a new full position (not currently held)
  ADD            — add size to an existing position (already held, thesis still valid)
  HOLD           — keep current position unchanged, thesis intact
  TRIM           — reduce size on an existing position (partial profit-take or risk reduction)
  SELL           — exit an existing position entirely (thesis broken or target reached)
  TIGHTEN_STOP   — raise the stop-loss on an existing position (protect gains)
  LOOSEN_STOP    — widen the stop-loss on an existing position (absorb volatility)
  REBALANCE      — adjust position weight to maintain target allocation
  WATCH          — no action, monitor for a better entry or more data

Return JSON only with keys: action, conviction_1_to_10, thesis, entry_zone, profit_target, stop_loss, position_size_pct, bear_case, rationale, data_gaps."""


def _build_decision_artifact(
    ctx: dict,
    ticker: str,
    *,
    bull: dict,
    bear: dict,
    risk_manager: dict,
    compliance: dict,
    ceo: dict,
) -> dict:
    return {
        "generated_at": ctx["generated_at"],
        "ticker": ticker,
        "bull": bull,
        "bear": bear,
        "risk_manager": risk_manager,
        "cro": risk_manager,
        "compliance": compliance,
        "ceo": ceo,
    }


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

    tracer.event(step="risk_manager", thought="risk gate and sizing constraints")
    risk_manager = chat_json(api_key=api_key, model=MODEL_FAST, system=SYSTEM_RISK_MANAGER, user={"context": ctx, "bull": bull, "bear": bear})

    tracer.event(step="compliance", thought="audit evidence and assumptions")
    compliance = chat_json(
        api_key=api_key,
        model=MODEL_FAST,
        system=SYSTEM_COMPLIANCE,
        user={"context": ctx, "bull": bull, "bear": bear, "risk_manager": risk_manager},
    )

    tracer.event(step="ceo", thought="final decision memo")
    ceo = chat_json(
        api_key=api_key,
        model=MODEL_DECISION,
        system=SYSTEM_CEO,
        user={"context": ctx, "bull": bull, "bear": bear, "risk_manager": risk_manager, "compliance": compliance},
    )

    pub = public_dir()
    pub.mkdir(parents=True, exist_ok=True)

    artifact = _build_decision_artifact(
        ctx,
        ticker,
        bull=bull,
        bear=bear,
        risk_manager=risk_manager,
        compliance=compliance,
        ceo=ceo,
    )

    latest_path = pub / "decision-latest.json"
    _atomic_write_json(latest_path, artifact)

    archive_dir = pub / "decisions"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{ticker}-{ctx['generated_at'].replace(':','-')}.json"
    _atomic_write_json(archive_path, artifact)
    _prune_decision_archive(archive_dir)

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

    _update_approval_queue(pub, ticker, ceo, ctx["generated_at"])

    tracer.finalize(status="success", summary=f"decision memo generated for {ticker}", artifact_written="decision-latest.json")
    print(json.dumps({"latest": str(latest_path), "archive": str(archive_path), "run_id": tracer.run_id}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
