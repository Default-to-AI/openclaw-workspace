from __future__ import annotations

import argparse
import json
from pathlib import Path

from axe_coo.step2_analysis import run_parallel_analysis
from axe_coo.util.env import load_project_env


def main() -> None:
    parser = argparse.ArgumentParser(prog="axe-step2-analyze")
    parser.add_argument("bundle_path")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()

    load_project_env()
    from os import getenv

    api_key = getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY missing in project .env")

    bundle_path = Path(args.bundle_path).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else bundle_path.parent / "step2-memos"
    out_dir.mkdir(parents=True, exist_ok=True)

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    result = __import__("asyncio").run(run_parallel_analysis(bundle=bundle, api_key=api_key))

    combined_path = out_dir / f"{bundle.get('ticker', 'ticker').lower()}-step2-analysis.json"
    combined_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    for item in result["results"]:
        memo_path = out_dir / f"{bundle.get('ticker', 'ticker').lower()}-{item['analyst']}-memo.json"
        memo_path.write_text(json.dumps(item["memo"], ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "bundle_path": str(bundle_path),
        "out_dir": str(out_dir),
        **result,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
