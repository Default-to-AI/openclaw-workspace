from __future__ import annotations

import os

from dotenv import load_dotenv

from axe_core.paths import project_root
from axe_technical.agent import run_technical_analysis


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="axe-technical")
    parser.add_argument("ticker", help="Ticker symbol, e.g. GOOG")
    parser.add_argument("--force", action="store_true", help="Force refresh")
    args = parser.parse_args(argv)

    load_dotenv(project_root() / ".env", override=False)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set")

    result = run_technical_analysis(args.ticker.upper(), api_key, args.force)
    print(f"Report written: {result['json_path']}")
    print(f"MD Report: {result['md_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
