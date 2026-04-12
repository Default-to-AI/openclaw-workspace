from __future__ import annotations

import argparse
import json
from pathlib import Path

from axe_coo.step3_decision import run_step3_decision
from axe_coo.util.env import load_project_env, project_root


def main() -> None:
    parser = argparse.ArgumentParser(prog="axe-step3-decide")
    parser.add_argument("step2_analysis_path")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument(
        "--investor-profile",
        default=str(project_root() / "INVESTOR_PROFILE.md"),
        help="Path to INVESTOR_PROFILE.md",
    )
    args = parser.parse_args()

    load_project_env()
    from os import getenv

    api_key = getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY missing in project .env")

    step2_path = Path(args.step2_analysis_path).resolve()
    investor_profile_path = Path(args.investor_profile).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else step2_path.parent / "step3-decision"
    out_dir.mkdir(parents=True, exist_ok=True)

    step2_analysis = json.loads(step2_path.read_text(encoding="utf-8"))
    investor_profile_text = investor_profile_path.read_text(encoding="utf-8")
    result = __import__("asyncio").run(
        run_step3_decision(
            step2_analysis=step2_analysis,
            investor_profile_text=investor_profile_text,
            api_key=api_key,
        )
    )

    ticker = str(result.get("ticker") or "ticker").lower()
    combined_path = out_dir / f"{ticker}-step3-decision.json"
    memo_path = out_dir / f"{ticker}-decision-memo.md"
    bull_path = out_dir / f"{ticker}-bull-case.json"
    bear_path = out_dir / f"{ticker}-bear-case.json"
    debate_path = out_dir / f"{ticker}-debate-summary.json"
    cio_path = out_dir / f"{ticker}-cio-proposal.json"
    cro_path = out_dir / f"{ticker}-cro-review.json"
    ceo_path = out_dir / f"{ticker}-ceo-decision.json"

    combined_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    memo_path.write_text(result["final_memo_markdown"], encoding="utf-8")
    bull_path.write_text(json.dumps(result["bull"]["memo"], ensure_ascii=False, indent=2), encoding="utf-8")
    bear_path.write_text(json.dumps(result["bear"]["memo"], ensure_ascii=False, indent=2), encoding="utf-8")
    debate_path.write_text(json.dumps(result["debate"]["memo"], ensure_ascii=False, indent=2), encoding="utf-8")
    cio_path.write_text(json.dumps(result["cio"]["memo"], ensure_ascii=False, indent=2), encoding="utf-8")
    cro_path.write_text(json.dumps(result["cro"]["memo"], ensure_ascii=False, indent=2), encoding="utf-8")
    ceo_path.write_text(json.dumps(result["ceo"]["memo"], ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "step2_analysis_path": str(step2_path),
                "investor_profile_path": str(investor_profile_path),
                "out_dir": str(out_dir),
                **result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
