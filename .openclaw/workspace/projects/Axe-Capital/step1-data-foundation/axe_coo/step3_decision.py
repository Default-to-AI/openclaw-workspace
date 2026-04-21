from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from axe_coo.util.numbers import safe_float as _safe_float

READ_PROFILE_RULE = (
    "Read INVESTOR_PROFILE.md before every decision. All recommendations must be consistent with "
    "Robert's profile, constraints, and current portfolio state."
)
OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_GENERAL_MODEL = "gpt-4.1-mini"
DEFAULT_CEO_MODEL = "gpt-4.1-mini"

@dataclass(frozen=True)
class StageSpec:
    name: str
    role: str
    model: str
    system_prompt: str
    max_tokens: int = 600


BULL_SPEC = StageSpec(
    name="bull",
    role="Bull Researcher",
    model=DEFAULT_GENERAL_MODEL,
    system_prompt=(
        f"You are Axe Capital's Bull Researcher. {READ_PROFILE_RULE} "
        "Build the strongest possible long case using only the provided Step 2 analyst memos, investor profile, "
        "and framework summary. Return strict JSON only, no markdown. "
        "Required keys: ticker, stance, core_thesis, best_arguments, catalysts, rebuttals_to_bear, confidence_1_to_10. "
        "best_arguments, catalysts, rebuttals_to_bear must be arrays of concise strings."
    ),
    max_tokens=800,
)

BEAR_SPEC = StageSpec(
    name="bear",
    role="Bear Researcher",
    model=DEFAULT_GENERAL_MODEL,
    system_prompt=(
        f"You are Axe Capital's Bear Researcher. {READ_PROFILE_RULE} "
        "Build the strongest possible case against the trade using only the provided Step 2 analyst memos, investor profile, "
        "and framework summary. Return strict JSON only, no markdown. "
        "Required keys: ticker, stance, core_thesis, best_arguments, failure_modes, rebuttals_to_bull, confidence_1_to_10. "
        "best_arguments, failure_modes, rebuttals_to_bull must be arrays of concise strings."
    ),
    max_tokens=800,
)

DEBATE_SPEC = StageSpec(
    name="debate",
    role="Debate Facilitator",
    model=DEFAULT_GENERAL_MODEL,
    system_prompt=(
        f"You are Axe Capital's Debate Facilitator. {READ_PROFILE_RULE} "
        "Read the bull and bear cases and summarize the two-round debate. Return strict JSON only. "
        "Required keys: ticker, winner, conclusive, summary, pro_bull_points, pro_bear_points, unresolved_questions, recommended_bias. "
        "winner must be bull, bear, or tie. conclusive must be boolean. recommended_bias must be bullish, bearish, or neutral. "
        "pro_bull_points, pro_bear_points, unresolved_questions must be arrays of concise strings."
    ),
    max_tokens=800,
)

CIO_SPEC = StageSpec(
    name="cio",
    role="CIO / Portfolio Manager",
    model=DEFAULT_GENERAL_MODEL,
    system_prompt=(
        f"You are Axe Capital's CIO / Portfolio Manager. {READ_PROFILE_RULE} "
        "Convert the analyst memos, investor profile, framework summary, and debate output into a trade proposal. "
        "Respect concentration, correlation, cash, and existing underwater positions. Return strict JSON only. "
        "Required keys: ticker, action_candidate, conviction_1_to_10, thesis, why_now, benchmark_case, entry_zone, stop_loss, "
        "take_profit_zone, position_size_pct_ibkr, portfolio_fit, key_risks. action_candidate must be BUY, HOLD, or PASS. "
        "entry_zone and take_profit_zone must be objects with low and high numeric-or-null fields. stop_loss must be numeric-or-null. "
        "portfolio_fit and key_risks must be arrays of concise strings."
    ),
    max_tokens=900,
)

CEO_SPEC = StageSpec(
    name="ceo",
    role="CEO / Decision Synthesizer",
    model=DEFAULT_CEO_MODEL,
    system_prompt=(
        f"You are Axe Capital's CEO / Decision Synthesizer. {READ_PROFILE_RULE} "
        "You MUST apply the full 6-step decision framework from INVESTOR_PROFILE.md before every decision: "
        "(1) portfolio health check, including hishtalmut status, underwater positions, cash floor, and sector concentration; "
        "(2) weighted scoring using Fundamental 35%, Macro 25%, Technical 20%, Sentiment 20%; "
        "(3) minimum threshold 6.5/10 to proceed; "
        "(4) conviction-based position sizing; "
        "(5) VIX-based market regime rules; "
        "(6) sector favor/avoid rules. "
        "Before any new IBKR trade, flag the hishtalmut priority rule with 2026 remaining contribution room of ₪19,800 unless conviction is 9+. "
        "If CRO blocks the trade, the final action cannot be BUY. "
        "Return strict JSON only, no markdown. Required keys: date, ticker, company_name, action, conviction_1_to_10, weighted_score, thesis, "
        "entry_zone, profit_target, stop_loss, position_size_pct, supporting_data, bear_case, portfolio_health_flags, decision_rationale, risk_gate, follow_up_actions. "
        "action must be BUY, HOLD, or PASS. supporting_data must be an object with fundamental, technical, sentiment, and macro keys. "
        "bear_case, portfolio_health_flags, decision_rationale, follow_up_actions must be arrays of concise strings."
    ),
    max_tokens=1400,
)



def _round(value: float | None, digits: int = 2) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def _extract_single(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def _extract_table_lines(text: str, heading: str, stop_marker: str) -> list[str]:
    lines = text.splitlines()
    start_index: int | None = None
    stop_index: int | None = None

    for idx, line in enumerate(lines):
        if line.strip() == heading.strip():
            start_index = idx + 1
            break

    if start_index is None:
        return []

    for idx in range(start_index, len(lines)):
        if lines[idx].strip().startswith(stop_marker.strip()):
            stop_index = idx
            break

    table_slice = lines[start_index:stop_index]
    return [line for line in table_slice if line.strip().startswith("|")]


def _parse_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _parse_holdings(profile_text: str) -> list[dict[str, Any]]:
    lines = _extract_table_lines(
        profile_text,
        "### IBKR Holdings — Current Positions",
        "**IBKR NAV**",
    )
    rows: list[dict[str, Any]] = []
    for line in lines[2:]:
        cells = _parse_markdown_row(line)
        if len(cells) < 8:
            continue
        rows.append(
            {
                "symbol": cells[0],
                "shares": cells[1],
                "avg_cost": _safe_float(cells[2].replace("$", "")),
                "market_value": _safe_float(cells[4].replace("$", "")),
                "upl_pct": _safe_float(cells[6]),
                "notes": cells[7],
            }
        )
    return rows


def _extract_profile_snapshot(profile_text: str, ticker: str, step2_analysis: dict[str, Any]) -> dict[str, Any]:
    holdings = _parse_holdings(profile_text)
    held_symbols = [row["symbol"] for row in holdings if row["symbol"] and row["symbol"] != "Cash"]
    holding_by_symbol = {row["symbol"]: row for row in holdings if row["symbol"]}
    underwater_positions = [
        row["symbol"]
        for row in holdings
        if row["symbol"] not in {"", "Cash"} and (row.get("upl_pct") is not None and row["upl_pct"] <= -10)
    ]

    ibkr_nav_usd = _safe_float(_extract_single(profile_text, r"\*\*IBKR NAV\*\*: \$([0-9,]+(?:\.[0-9]+)?)"))
    cash_usd = _safe_float(_extract_single(profile_text, r"\*\*Cash\*\*: \$([0-9,]+(?:\.[0-9]+)?)"))
    positions_in_loss = _safe_float(_extract_single(profile_text, r"\*\*Positions in loss\*\*: ([0-9]+) of [0-9]+"))
    tech_exposure_pct = _safe_float(
        _extract_single(profile_text, r"\| US Large Cap Tech \| ~?([0-9]+(?:\.[0-9]+)?)%\+? \|")
    )
    annual_ceiling_ils = _safe_float(_extract_single(profile_text, r"Annual ceiling: ₪([0-9,]+(?:\.[0-9]+)?)/year"))
    hishtalmut_remaining_ils = _safe_float(
        _extract_single(profile_text, r"2026 remaining contribution room: \*\*₪([0-9,]+)\*\*")
    ) or 0.0
    max_position_pct = _safe_float(
        _extract_single(profile_text, r"Maximum single new position: ([0-9]+(?:\.[0-9]+)?)% of IBKR NAV")
    ) or 15.0
    min_position_usd = _safe_float(
        _extract_single(profile_text, r"Minimum position size worth adding: \$([0-9,]+(?:\.[0-9]+)?)")
    ) or 2000.0
    cash_floor_usd = _safe_float(
        _extract_single(profile_text, r"Cash floor: maintain minimum \$([0-9,]+(?:\.[0-9]+)?) cash")
    ) or 5000.0

    memo_blob = json.dumps(step2_analysis, ensure_ascii=False).lower()
    overlap_keywords = [
        "technology",
        "software",
        "semiconductor",
        "cloud",
        "ai",
        "internet",
        "iphone",
        "smartphone",
        "big tech",
    ]
    adds_to_overweight_sector = bool(tech_exposure_pct and tech_exposure_pct > 50 and any(k in memo_blob for k in overlap_keywords))

    ticker_holding = holding_by_symbol.get(ticker)
    ticker_is_loser = bool(ticker_holding and (ticker_holding.get("upl_pct") or 0) < 0)

    return {
        "ibkr_nav_usd": ibkr_nav_usd,
        "cash_usd": cash_usd,
        "cash_floor_usd": cash_floor_usd,
        "positions_in_loss": int(positions_in_loss or 0),
        "underwater_positions_gt_10pct": underwater_positions,
        "underwater_count_gt_10pct": len(underwater_positions),
        "held_symbols": held_symbols,
        "ticker_already_held": ticker in held_symbols,
        "ticker_is_loser": ticker_is_loser,
        "large_cap_tech_exposure_pct": tech_exposure_pct,
        "adds_to_overweight_sector": adds_to_overweight_sector,
        "hishtalmut_annual_ceiling_ils": annual_ceiling_ils,
        "hishtalmut_remaining_ils_2026": hishtalmut_remaining_ils,
        "hishtalmut_maxed_for_year": hishtalmut_remaining_ils <= 0,
        "max_new_position_pct": max_position_pct,
        "min_new_position_usd": min_position_usd,
        "default_stop_loss_pct": 10.0,
    }


def _get_stage_memo(step2_analysis: dict[str, Any], analyst_name: str) -> dict[str, Any]:
    for item in step2_analysis.get("results", []):
        if item.get("analyst") == analyst_name:
            return item.get("memo") or {}
    return {}


def _extract_vix_from_macro(macro_memo: dict[str, Any]) -> float | None:
    macro_regime = macro_memo.get("macro_regime")
    regime_volatility = macro_regime.get("volatility") if isinstance(macro_regime, dict) else None
    candidates = [
        regime_volatility,
        macro_memo.get("macro_thesis"),
        json.dumps(macro_memo, ensure_ascii=False),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        match = re.search(r"VIX[^0-9]*([0-9]+(?:\.[0-9]+)?)", str(candidate), re.IGNORECASE)
        if match:
            return _safe_float(match.group(1))
    return None


def _position_size_band(weighted_score: float) -> tuple[float, float]:
    if weighted_score >= 9:
        return (12.0, 15.0)
    if weighted_score >= 7:
        return (7.0, 10.0)
    if weighted_score >= 6.5:
        return (3.0, 5.0)
    return (0.0, 0.0)


def _market_regime(vix: float | None) -> dict[str, Any]:
    if vix is None:
        return {
            "vix": None,
            "regime": "unknown",
            "posture": "unknown",
            "size_multiplier": 1.0,
            "requires_9_plus": False,
            "notes": ["VIX unavailable, so regime is inferred conservatively."],
        }
    if vix < 15:
        return {
            "vix": vix,
            "regime": "normal",
            "posture": "Normal. Full position sizing.",
            "size_multiplier": 1.0,
            "requires_9_plus": False,
            "notes": ["VIX below 15, normal risk regime."],
        }
    if vix <= 25:
        return {
            "vix": vix,
            "regime": "cautious",
            "posture": "Cautious. Reduce new entries by 20%.",
            "size_multiplier": 0.8,
            "requires_9_plus": False,
            "notes": ["VIX between 15 and 25, reduce new entries by 20%."],
        }
    if vix <= 35:
        return {
            "vix": vix,
            "regime": "defensive",
            "posture": "Defensive. Only 9+ conviction trades.",
            "size_multiplier": 0.7,
            "requires_9_plus": True,
            "notes": ["VIX between 25 and 35, only 9+ conviction trades qualify."],
        }
    return {
        "vix": vix,
        "regime": "accumulation",
        "posture": "Accumulation mode. Surface the best opportunities aggressively.",
        "size_multiplier": 1.0,
        "requires_9_plus": False,
        "notes": ["VIX above 35, Robert's profile shifts into dip-buying mode."],
    }


def _supporting_data(step2_analysis: dict[str, Any]) -> dict[str, Any]:
    fundamental = _get_stage_memo(step2_analysis, "fundamental")
    technical = _get_stage_memo(step2_analysis, "technical")
    sentiment = _get_stage_memo(step2_analysis, "sentiment")
    macro = _get_stage_memo(step2_analysis, "macro")
    return {
        "fundamental": {
            "score": _safe_float(fundamental.get("score_1_to_10")),
            "summary": fundamental.get("thesis"),
        },
        "technical": {
            "score": _safe_float(technical.get("score_1_to_10")),
            "summary": technical.get("setup") or technical.get("trend"),
        },
        "sentiment": {
            "score": _safe_float(sentiment.get("score_1_to_10")),
            "summary": sentiment.get("narrative_summary"),
        },
        "macro": {
            "score": _safe_float(macro.get("score_1_to_10")),
            "summary": macro.get("macro_thesis"),
            "tide_in_or_out": macro.get("tide_in_or_out"),
        },
    }


def _compact_step2_context(step2_analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": step2_analysis.get("ticker"),
        "analyst_memos": {
            item.get("analyst"): item.get("memo")
            for item in step2_analysis.get("results", [])
        },
    }


def _investor_profile_context(profile_text: str, framework: dict[str, Any]) -> dict[str, Any]:
    profile = framework["profile_snapshot"]
    return {
        "read_rule": READ_PROFILE_RULE,
        "investor_style": "Aggressive accumulator, fundamentals-first, analytical, no leverage, no margin, no emotional selling.",
        "ibkr_nav_usd": profile["ibkr_nav_usd"],
        "cash_usd": profile["cash_usd"],
        "cash_floor_usd": profile["cash_floor_usd"],
        "held_symbols": profile["held_symbols"],
        "underwater_positions_gt_10pct": profile["underwater_positions_gt_10pct"],
        "large_cap_tech_exposure_pct": profile["large_cap_tech_exposure_pct"],
        "hishtalmut_remaining_ils_2026": profile["hishtalmut_remaining_ils_2026"],
        "max_new_position_pct": profile["max_new_position_pct"],
        "min_new_position_usd": profile["min_new_position_usd"],
        "default_stop_loss_pct": profile["default_stop_loss_pct"],
        "favor": [
            "mid-cap or international names with less index overlap",
            "event-driven setups",
            "underrepresented sectors like healthcare, energy, industrials, consumer",
        ],
        "avoid": [
            "more US mega-cap tech",
            "broad index ETFs already replicated in passive accounts",
        ],
        "source_excerpt": profile_text[:2500],
    }


def build_framework(step2_analysis: dict[str, Any], investor_profile_text: str, raw_bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    ticker = step2_analysis.get("ticker") or "UNKNOWN"
    supporting_data = _supporting_data(step2_analysis)
    scores = {
        name: _safe_float(data.get("score")) or 0.0
        for name, data in supporting_data.items()
    }
    weights = {
        "fundamental": 0.35,
        "macro": 0.25,
        "technical": 0.20,
        "sentiment": 0.20,
    }
    weighted_score = round(sum(scores[name] * weights[name] for name in weights), 2)
    profile_snapshot = _extract_profile_snapshot(investor_profile_text, ticker=ticker, step2_analysis=step2_analysis)
    macro_memo = _get_stage_memo(step2_analysis, "macro")
    vix: float | None = None
    if raw_bundle is not None:
        macro_series = (raw_bundle.get("macro") or {}).get("VIXCLS") or []
        if macro_series:
            vix = _safe_float((macro_series[0] or {}).get("value"))
    if vix is None:
        vix = _extract_vix_from_macro(macro_memo)
    regime = _market_regime(vix)
    base_low, base_high = _position_size_band(weighted_score)
    base_mid = round((base_low + base_high) / 2, 2) if base_high else 0.0

    size_multiplier = regime["size_multiplier"]
    sizing_adjustments: list[dict[str, Any]] = []
    if regime["size_multiplier"] != 1.0:
        sizing_adjustments.append({
            "reason": regime["posture"],
            "multiplier": regime["size_multiplier"],
        })
    if profile_snapshot["underwater_count_gt_10pct"] > 3:
        size_multiplier *= 0.7
        sizing_adjustments.append({
            "reason": f"{profile_snapshot['underwater_count_gt_10pct']} existing positions are more than 10% underwater.",
            "multiplier": 0.7,
        })
    if profile_snapshot["ticker_already_held"]:
        size_multiplier *= 0.7
        sizing_adjustments.append({
            "reason": f"{ticker} is already held, so add-on size must be reduced.",
            "multiplier": 0.7,
        })
    if all(scores[name] >= 7 for name in weights) and (supporting_data["macro"].get("tide_in_or_out") == "out"):
        size_multiplier *= 0.7
        sizing_adjustments.append({
            "reason": "All analyst scores are bullish but macro tide is out.",
            "multiplier": 0.7,
        })

    suggested_position_size_pct = round(base_mid * size_multiplier, 2) if base_mid else 0.0
    suggested_position_value_usd = round((profile_snapshot["ibkr_nav_usd"] or 0) * suggested_position_size_pct / 100, 2)

    health_flags = []
    if not profile_snapshot["hishtalmut_maxed_for_year"]:
        health_flags.append(
            f"Hishtalmut still has ₪{int(profile_snapshot['hishtalmut_remaining_ils_2026']):,} of 2026 room remaining."
        )
    if profile_snapshot["underwater_count_gt_10pct"] > 3:
        health_flags.append(
            f"{profile_snapshot['underwater_count_gt_10pct']} positions are already more than 10% underwater."
        )
    if (profile_snapshot["cash_usd"] or 0) < (profile_snapshot["cash_floor_usd"] or 0):
        health_flags.append("Cash is below the required liquidity floor.")
    if profile_snapshot["adds_to_overweight_sector"]:
        health_flags.append("This idea adds to an already overweight US large-cap tech concentration.")

    return {
        "ticker": ticker,
        "weights": weights,
        "scores": scores,
        "weighted_score": weighted_score,
        "minimum_threshold": 6.5,
        "high_conviction_threshold": 8.0,
        "profile_snapshot": profile_snapshot,
        "market_regime": regime,
        "base_position_size_band_pct": {"low": base_low, "high": base_high},
        "suggested_position_size_pct": suggested_position_size_pct,
        "suggested_position_value_usd": suggested_position_value_usd,
        "sizing_adjustments": sizing_adjustments,
        "health_flags": health_flags,
        "supporting_data": supporting_data,
    }


def _json_payload(**kwargs: Any) -> str:
    return json.dumps(kwargs, ensure_ascii=False, indent=2)


def _stage_user_prompt(spec: StageSpec, payload: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": spec.system_prompt},
        {
            "role": "user",
            "content": (
                f"Role: {spec.role}\n"
                "Use only the supplied inputs. If something is missing, say so inside the JSON instead of inventing facts.\n"
                "Return valid JSON only.\n\n"
                f"Inputs:\n{_json_payload(**payload)}"
            ),
        },
    ]


async def _call_openai_json(
    client: httpx.AsyncClient,
    api_key: str,
    spec: StageSpec,
    payload: dict[str, Any],
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
            "max_tokens": spec.max_tokens,
            "response_format": {"type": "json_object"},
            "messages": _stage_user_prompt(spec, payload),
        },
    )
    response.raise_for_status()
    raw = response.json()
    message = raw["choices"][0]["message"]["content"]
    memo = json.loads(message)
    return {
        "stage": spec.name,
        "role": spec.role,
        "model": spec.model,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "memo": memo,
        "usage": raw.get("usage"),
    }


def _crop_profile_text(profile_text: str) -> str:
    return profile_text[:12000]


def _extract_entry_zone(memo: dict[str, Any]) -> dict[str, Any]:
    zone = memo.get("entry_zone") or {}
    return {
        "low": _safe_float(zone.get("low")),
        "high": _safe_float(zone.get("high")),
    }


def _extract_target_zone(memo: dict[str, Any]) -> dict[str, Any]:
    zone = memo.get("take_profit_zone") or memo.get("profit_target") or {}
    if isinstance(zone, dict):
        return {
            "low": _safe_float(zone.get("low") or zone.get("price")),
            "high": _safe_float(zone.get("high") or zone.get("price")),
        }
    return {"low": None, "high": None}


def run_cro_review(framework: dict[str, Any], cio_memo: dict[str, Any]) -> dict[str, Any]:
    profile = framework["profile_snapshot"]
    weighted_score = framework["weighted_score"]
    conviction = _safe_float(cio_memo.get("conviction_1_to_10")) or weighted_score
    action_candidate = str(cio_memo.get("action_candidate") or "PASS").upper()
    position_size_pct = _safe_float(cio_memo.get("position_size_pct_ibkr")) or framework["suggested_position_size_pct"]
    stop_loss = _safe_float(cio_memo.get("stop_loss"))
    projected_value_usd = round((profile["ibkr_nav_usd"] or 0) * (position_size_pct or 0) / 100, 2)
    projected_cash_after = round((profile["cash_usd"] or 0) - projected_value_usd, 2)

    blockers: list[str] = []
    conditions: list[str] = []

    if action_candidate == "BUY":
        if weighted_score < framework["minimum_threshold"]:
            blockers.append(f"Weighted score {weighted_score}/10 is below the 6.5 threshold.")
        if not profile["hishtalmut_maxed_for_year"] and conviction < 9:
            blockers.append(
                f"Hishtalmut still has ₪{int(profile['hishtalmut_remaining_ils_2026']):,} remaining for 2026, so IBKR deployment is deprioritized unless conviction is 9+."
            )
        if profile["underwater_count_gt_10pct"] > 3 and conviction < 9:
            blockers.append(
                f"{profile['underwater_count_gt_10pct']} existing positions are already more than 10% underwater, so new entries require 9+ conviction."
            )
        if (profile["cash_usd"] or 0) < (profile["cash_floor_usd"] or 0):
            blockers.append("Cash is already below the $5,000 floor.")
        if projected_cash_after < (profile["cash_floor_usd"] or 0):
            blockers.append(
                f"Projected post-trade cash ${projected_cash_after:,.2f} would fall below the ${profile['cash_floor_usd']:,.0f} floor."
            )
        if framework["market_regime"]["requires_9_plus"] and conviction < 9:
            blockers.append(
                f"Current VIX regime is {framework['market_regime']['regime']}, which only permits 9+ conviction trades."
            )
        if (position_size_pct or 0) > (profile["max_new_position_pct"] or 15):
            blockers.append(
                f"Proposed size {position_size_pct}% exceeds the max {profile['max_new_position_pct']}% single-position cap."
            )
        if projected_value_usd < (profile["min_new_position_usd"] or 2000):
            blockers.append(
                f"Projected trade value ${projected_value_usd:,.2f} is below the minimum worthwhile size of ${profile['min_new_position_usd']:,.0f}."
            )
        if stop_loss is None:
            blockers.append("Every new entry requires a stop-loss.")
        if profile["ticker_is_loser"] and conviction < 9:
            blockers.append("Do not add to losing positions unless conviction is 9+ and thesis is reconfirmed.")
        if profile["adds_to_overweight_sector"]:
            conditions.append("Trade adds to an already overweight US large-cap tech concentration.")

    if action_candidate == "HOLD":
        if profile["ticker_is_loser"] and stop_loss is None:
            blockers.append(
                "HOLD on an underwater position requires a confirmed stop-loss level."
            )

    gate = "BLOCKED" if blockers else ("CONDITIONAL" if conditions else "APPROVED")
    allowed_action = "PASS" if gate == "BLOCKED" and action_candidate == "BUY" else action_candidate
    return {
        "ticker": framework["ticker"],
        "gate": gate,
        "allowed_action": allowed_action,
        "blockers": blockers,
        "conditions": conditions,
        "projected_trade_value_usd": projected_value_usd,
        "projected_cash_after_usd": projected_cash_after,
    }


def render_ceo_memo(ceo_memo: dict[str, Any]) -> str:
    entry_zone = ceo_memo.get("entry_zone") or {}
    if not isinstance(entry_zone, dict):
        entry_zone = {"low": _safe_float(entry_zone), "high": _safe_float(entry_zone)}

    profit_target = ceo_memo.get("profit_target") or {}
    if not isinstance(profit_target, dict):
        profit_target = {"price": _safe_float(profit_target), "upside_pct": None, "timeframe": None}

    stop_loss = ceo_memo.get("stop_loss") or {}
    if not isinstance(stop_loss, dict):
        stop_loss = {"price": _safe_float(stop_loss), "downside_pct": None}

    supporting = ceo_memo.get("supporting_data") or {}

    def zone_text(zone: dict[str, Any]) -> str:
        low = zone.get("low")
        high = zone.get("high")
        if low is None and high is None:
            return "n/a"
        if low is None:
            return f"${high}"
        if high is None or high == low:
            return f"${low}"
        return f"${low} – ${high}"

    stop_loss_text = "n/a"
    if stop_loss:
        price = stop_loss.get("price")
        downside = stop_loss.get("downside_pct")
        if price is not None and downside is not None:
            stop_loss_text = f"${price} ({downside}% max loss)"
        elif price is not None:
            stop_loss_text = f"${price}"

    bear_case_lines = "\n".join(f"• {item}" for item in (ceo_memo.get("bear_case") or [])) or "• n/a"
    rationale_lines = "\n".join(f"• {item}" for item in (ceo_memo.get("decision_rationale") or [])) or "• n/a"
    health_lines = "\n".join(f"• {item}" for item in (ceo_memo.get("portfolio_health_flags") or [])) or "• n/a"

    return (
        "═══════════════════════════════════════════════\n"
        "AXE CAPITAL — DECISION MEMO\n"
        "═══════════════════════════════════════════════\n"
        f"DATE: {ceo_memo.get('date')}\n"
        f"TICKER: {ceo_memo.get('ticker')} | {ceo_memo.get('company_name')}\n"
        f"ACTION: {ceo_memo.get('action')}\n"
        f"CONVICTION: {ceo_memo.get('conviction_1_to_10')}\n"
        "───────────────────────────────────────────────\n"
        "THESIS\n"
        f"{ceo_memo.get('thesis')}\n\n"
        f"WEIGHTED SCORE: {ceo_memo.get('weighted_score')}\n"
        f"ENTRY ZONE:    {zone_text(entry_zone)}\n"
        f"PROFIT TARGET: {zone_text({'low': profit_target.get('low', profit_target.get('price')), 'high': profit_target.get('high', profit_target.get('price'))})} ({profit_target.get('upside_pct')}% upside, {profit_target.get('timeframe')})\n"
        f"STOP-LOSS:     {stop_loss_text}\n"
        f"POSITION SIZE: {ceo_memo.get('position_size_pct')}% of portfolio\n"
        "───────────────────────────────────────────────\n"
        "SUPPORTING DATA\n"
        f"• Fundamental: {supporting.get('fundamental', {}).get('score')} — {supporting.get('fundamental', {}).get('summary')}\n"
        f"• Technical:   {supporting.get('technical', {}).get('score')} — {supporting.get('technical', {}).get('summary')}\n"
        f"• Sentiment:   {supporting.get('sentiment', {}).get('score')} — {supporting.get('sentiment', {}).get('summary')}\n"
        f"• Macro:       {supporting.get('macro', {}).get('score')} — {supporting.get('macro', {}).get('summary')}\n"
        "───────────────────────────────────────────────\n"
        "PORTFOLIO HEALTH FLAGS\n"
        f"{health_lines}\n"
        "───────────────────────────────────────────────\n"
        "BEAR CASE\n"
        f"{bear_case_lines}\n"
        "───────────────────────────────────────────────\n"
        "DECISION RATIONALE\n"
        f"{rationale_lines}\n"
        "───────────────────────────────────────────────\n"
        f"RISK GATE: {ceo_memo.get('risk_gate')}\n"
        "═══════════════════════════════════════════════\n"
    )


async def run_step3_decision(
    step2_analysis: dict[str, Any],
    investor_profile_text: str,
    api_key: str,
    timeout_seconds: float = 180.0,
    raw_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    local_date = datetime.now(ZoneInfo("Asia/Jerusalem")).date().isoformat()
    framework = build_framework(step2_analysis, investor_profile_text, raw_bundle=raw_bundle)
    profile_context = _investor_profile_context(investor_profile_text, framework)
    shared_payload = {
        "ticker": step2_analysis.get("ticker"),
        "investor_profile_path": "projects/Axe-Capital/INVESTOR_PROFILE.md",
        "investor_profile_context": profile_context,
        "framework": framework,
        "step2_analysis": _compact_step2_context(step2_analysis),
    }

    timeout = httpx.Timeout(timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        bull_stage, bear_stage = await asyncio.gather(
            _call_openai_json(client, api_key, BULL_SPEC, shared_payload),
            _call_openai_json(client, api_key, BEAR_SPEC, shared_payload),
        )

        follow_on_payload = {
            **shared_payload,
            "bull_case": bull_stage["memo"],
            "bear_case": bear_stage["memo"],
        }
        debate_stage, cio_stage = await asyncio.gather(
            _call_openai_json(client, api_key, DEBATE_SPEC, follow_on_payload),
            _call_openai_json(client, api_key, CIO_SPEC, follow_on_payload),
        )

        cro_stage = {
            "stage": "cro",
            "role": "CRO / Risk Officer",
            "model": "deterministic-rules",
            "elapsed_seconds": 0.0,
            "memo": run_cro_review(framework, cio_stage["memo"]),
            "usage": None,
        }

        ceo_payload = {
            **follow_on_payload,
            "debate_summary": debate_stage["memo"],
            "cio_trade_proposal": cio_stage["memo"],
            "cro_review": cro_stage["memo"],
            "date": local_date,
        }
        ceo_stage = await _call_openai_json(client, api_key, CEO_SPEC, ceo_payload)

    ceo_stage["memo"]["date"] = local_date
    ceo_stage["memo"].setdefault("ticker", step2_analysis.get("ticker"))
    ceo_stage["memo"].setdefault("weighted_score", framework["weighted_score"])
    ceo_stage["memo"].setdefault("position_size_pct", framework["suggested_position_size_pct"])
    ceo_stage["memo"].setdefault("supporting_data", framework["supporting_data"])
    ceo_stage["memo"]["risk_gate"] = cro_stage["memo"]["gate"]
    ceo_stage["memo"].setdefault("portfolio_health_flags", framework["health_flags"])

    final_result = {
        "ticker": step2_analysis.get("ticker"),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "framework": framework,
        "bull": bull_stage,
        "bear": bear_stage,
        "debate": debate_stage,
        "cio": cio_stage,
        "cro": cro_stage,
        "ceo": ceo_stage,
        "final_memo_markdown": render_ceo_memo(ceo_stage["memo"]),
    }
    return final_result
