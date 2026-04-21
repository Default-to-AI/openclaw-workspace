"""Project current dashboard artifacts into a normalized Command Center payload."""
from __future__ import annotations

import json
from pathlib import Path


WATCHER_KEYS = [
    ("news", "News Watcher"),
    ("alpha", "Value / Discount Watcher"),
]


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _status_from_health(health: dict, key: str) -> tuple[str, str | None]:
    artifact = (health.get("artifacts") or {}).get(key) or {}
    return artifact.get("status", "missing"), artifact.get("last_refresh")


def _mission_status(raw_status: str) -> str:
    mapping = {
        "success": "completed",
        "failed": "failed",
        "running": "running",
        "queued": "queued",
        "blocked": "blocked",
    }
    return mapping.get(raw_status or "", "running")


def build_mission_index(public: Path) -> dict:
    traces_index = _load_json(public / "traces" / "index.json")
    latest_by_run_id: dict[str, dict] = {}

    for run in traces_index.get("runs", []):
        if run.get("agent") != "committee":
            continue
        latest_by_run_id[run["run_id"]] = run

    missions = []
    for run_id, run in latest_by_run_id.items():
        missions.append(
            {
                "run_id": run_id,
                "status": _mission_status(run.get("status")),
                "started_at": run.get("started_at"),
                "updated_at": run.get("ended_at") or run.get("started_at"),
                "ended_at": run.get("ended_at"),
                "headline": run.get("summary") or "",
                "latest_summary": run.get("summary") or "",
            }
        )

    missions.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {
        "generated_at": traces_index.get("generated_at"),
        "missions": missions,
    }


def build_command_center_payload(public: Path) -> dict:
    health = _load_json(public / "health.json")
    portfolio = _load_json(public / "portfolio.json")
    position_state = _load_json(public / "position-state.json")
    decision = _load_json(public / "decision-latest.json")
    analyst_reports = _load_json(public / "analyst-reports" / "index.json")
    mission_index = build_mission_index(public)

    partial = False

    decision_inbox = []
    if decision.get("ticker") and decision.get("ceo_action"):
        decision_inbox.append(
            {
                "run_id": decision.get("run_id"),
                "symbol": decision.get("ticker"),
                "action": decision.get("ceo_action"),
                "confidence": decision.get("ceo_conviction"),
                "summary": decision.get("ceo_thesis"),
                "timestamp": decision.get("generated_at"),
                "candidate_type": decision.get("candidate_type"),
            }
        )

    surveillance_alerts = []
    states = position_state.get("positions") or {}
    for position in portfolio.get("positions", []):
        severity = position.get("alert_status")
        if not severity or severity == "GREEN":
            continue
        symbol = position.get("symbol")
        state = states.get(symbol, {})
        surveillance_alerts.append(
            {
                "symbol": symbol,
                "severity": severity,
                "distance_to_stop_pct": position.get("distance_to_stop_pct"),
                "stop_loss": state.get("stop_loss") or position.get("stop_loss_level"),
                "target_price": state.get("target_price"),
                "thesis": state.get("thesis"),
                "last_price": position.get("last_price") or position.get("last"),
            }
        )

    watchers = []
    reports_available = bool(analyst_reports)
    if not reports_available:
        partial = True

    for key, label in WATCHER_KEYS:
        status, last_refresh = _status_from_health(health, key)
        if not reports_available:
            status = "missing"
        watchers.append(
            {
                "key": key,
                "label": label,
                "status": status,
                "partial": status == "missing",
                "last_refresh": last_refresh,
            }
        )

    firm_exceptions = []
    for key, artifact in (health.get("artifacts") or {}).items():
        status = artifact.get("status")
        if status == "fresh":
            continue
        firm_exceptions.append(
            {
                "key": key,
                "status": status or "missing",
                "last_refresh": artifact.get("last_refresh"),
                "age_min": artifact.get("age_min"),
            }
        )
    firm_exceptions.sort(key=lambda item: (item["status"] != "missing", item.get("age_min") or 0), reverse=True)

    current_focus = mission_index["missions"][0] if mission_index["missions"] else None

    return {
        "generated_at": health.get("generated_at") or portfolio.get("generated_at") or decision.get("generated_at"),
        "partial": partial,
        "data_freshness": health.get("artifacts") or {},
        "decision_inbox": decision_inbox,
        "live_missions": mission_index["missions"],
        "watchers": watchers,
        "surveillance_alerts": surveillance_alerts,
        "firm_exceptions": firm_exceptions,
        "current_focus": current_focus,
    }


def write_command_center_artifacts(public: Path) -> None:
    payload = build_command_center_payload(public)
    mission_index = build_mission_index(public)

    command_center_path = public / "command-center.json"
    command_center_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    missions_dir = public / "missions"
    missions_dir.mkdir(parents=True, exist_ok=True)
    (missions_dir / "index.json").write_text(json.dumps(mission_index, indent=2), encoding="utf-8")
