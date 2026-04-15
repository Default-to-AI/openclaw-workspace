"""`axe` CLI: axe run alpha|news|portfolio|all"""
from __future__ import annotations

import argparse
import sys

from axe_orchestrator import runners

TARGET_NAMES = ("alpha", "news", "portfolio")


def _target(name: str) -> int:
    return getattr(runners, f"run_{name}")()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="axe")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="Run an agent")
    run.add_argument("target")

    args = parser.parse_args(argv)

    if args.cmd != "run":
        parser.error(f"unknown command: {args.cmd}")
        return 2

    if args.target not in TARGET_NAMES and args.target != "all":
        print(f"[axe] unknown target: {args.target}", file=sys.stderr)
        return 2

    if args.target == "all":
        failures = 0
        for name in ("portfolio", "alpha", "news"):
            rc = _target(name)
            print(f"[axe] {name} -> rc={rc}")
            if rc != 0:
                failures += 1
        return 0 if failures == 0 else 1

    return _target(args.target)


if __name__ == "__main__":
    sys.exit(main())
