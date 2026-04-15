from __future__ import annotations

import asyncio
import json

from axe_alpha.alpha_scan import report_path_for_date, run_alpha_hunter_scan
from axe_alpha.util import load_project_env, openai_api_key
from axe_core import Tracer
from axe_core.paths import public_dir


def main() -> None:
    load_project_env()
    api_key = openai_api_key()

    tracer = Tracer(agent="axe_alpha")
    tracer.start()
    tracer.event(step="load_env", thought="env loaded, key resolved")

    try:
        tracer.event(step="scan", thought="running alpha hunter scan")
        report = asyncio.run(run_alpha_hunter_scan(api_key=api_key))
    except Exception as exc:
        tracer.event(step="error", thought=f"scan failed: {exc}")
        tracer.finalize(status="failed", summary=f"scan failed: {exc}", artifact_written=None)
        raise

    report_date = report["report_date"]
    n_opps = len(report.get("top_opportunities", []))

    archive_path = report_path_for_date(report_date)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    latest = public_dir() / "alpha-latest.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    tmp = latest.with_name("alpha-latest.json.tmp")
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(latest)

    tracer.event(
        step="write_artifacts",
        thought=f"wrote archive {archive_path.name} and alpha-latest.json",
        io={"out": {"opportunities": n_opps}},
    )
    tracer.finalize(
        status="success",
        summary=f"scanned and surfaced {n_opps} opportunities",
        artifact_written="alpha-latest.json",
    )

    print(json.dumps({"report_path": str(archive_path), "latest": str(latest), **report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
