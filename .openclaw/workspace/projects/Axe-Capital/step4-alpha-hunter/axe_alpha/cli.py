from __future__ import annotations

import json
from pathlib import Path

from axe_alpha.alpha_scan import report_path_for_date, run_alpha_hunter_scan
from axe_alpha.util import load_project_env, openai_api_key


def main() -> None:
    load_project_env()
    api_key = openai_api_key()
    report = __import__("asyncio").run(run_alpha_hunter_scan(api_key=api_key))
    report_path = report_path_for_date(report["report_date"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report_path": str(report_path), **report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
