from __future__ import annotations

import json

from axe_decision.cli import _load_analyst_reports
from axe_decision.cli import _build_decision_artifact


def test_load_analyst_reports_reads_latest_index(tmp_path, monkeypatch):
    reports = tmp_path / "analyst-reports"
    reports.mkdir()
    (reports / "GOOG-technical.json").write_text(json.dumps({"agent": "technical"}), encoding="utf-8")
    (reports / "index.json").write_text(
        json.dumps({"symbols": {"GOOG": {"technical": {"json_path": "GOOG-technical.json"}}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr("axe_decision.cli.public_dir", lambda: tmp_path)

    loaded = _load_analyst_reports("goog")

    assert loaded["technical"]["agent"] == "technical"


def test_build_decision_artifact_includes_risk_compliance_and_cro_alias():
    artifact = _build_decision_artifact(
        {"generated_at": "2026-04-16T00:00:00Z"},
        "RTX",
        bull={"thesis": "buy"},
        bear={"thesis": "pass"},
        risk_manager={"gate": "CONDITIONAL"},
        compliance={"audit_status": "NEEDS_MORE_EVIDENCE"},
        ceo={"action": "HOLD"},
    )

    assert artifact["ticker"] == "RTX"
    assert artifact["risk_manager"]["gate"] == "CONDITIONAL"
    assert artifact["cro"] == artifact["risk_manager"]
    assert artifact["compliance"]["audit_status"] == "NEEDS_MORE_EVIDENCE"
