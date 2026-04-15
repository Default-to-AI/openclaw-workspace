"""`axe` CLI: axe run alpha|news|portfolio|all | axe health"""
from __future__ import annotations

import argparse
import sys

from axe_orchestrator import runners

TARGET_NAMES = tuple(runners.AGENT_ORDER)


def _target(name: str) -> int:
    return getattr(runners, f"run_{name}")()


def _refresh_health() -> None:
    from axe_orchestrator.health import write_health

    try:
        write_health()
    except Exception as exc:
        print(f"[axe] warning: failed to write health.json: {exc}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="axe")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="Run an agent")
    run.add_argument("target")
    sub.add_parser("health", help="Regenerate health.json from current artifacts")

    args = parser.parse_args(argv)

    if args.cmd == "health":
        from axe_orchestrator.health import write_health

        path = write_health()
        print(f"[axe] wrote {path}")
        return 0

    if args.cmd != "run":
        parser.error(f"unknown command: {args.cmd}")
        return 2

    if args.target not in TARGET_NAMES and args.target != "all":
        print(f"[axe] unknown target: {args.target}", file=sys.stderr)
        return 2

    if args.target == "all":
        failures = 0
        for name in runners.AGENT_ORDER:
            rc = _target(name)
            print(f"[axe] {name} -> rc={rc}")
            if rc != 0:
                failures += 1
        _refresh_health()
        return 0 if failures == 0 else 1

    rc = _target(args.target)
    _refresh_health()
    return rc


if __name__ == "__main__":
    sys.exit(main())
