from __future__ import annotations

import json

from axe_fundamental.reports import update_report_index


def test_update_report_index_records_latest_agent_path(tmp_path):
    reports_dir = tmp_path / "analyst-reports"
    reports_dir.mkdir()
    report_path = reports_dir / "GOOG-fundamental-2026-04-16T00-00-00Z.json"
    md_path = reports_dir / "GOOG-fundamental-2026-04-16T00-00-00Z.md"
    report_path.write_text("{}", encoding="utf-8")
    md_path.write_text("# GOOG", encoding="utf-8")

    index = update_report_index(reports_dir, "goog", "fundamental", report_path, md_path)

    latest = index["symbols"]["GOOG"]["fundamental"]
    assert latest["json_path"] == "GOOG-fundamental-2026-04-16T00-00-00Z.json"
    assert latest["md_path"] == "GOOG-fundamental-2026-04-16T00-00-00Z.md"
    assert json.loads((reports_dir / "index.json").read_text(encoding="utf-8")) == index
