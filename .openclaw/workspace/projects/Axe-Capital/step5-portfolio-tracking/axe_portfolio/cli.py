from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from axe_core import Tracer
from axe_portfolio.tracker import run_portfolio_review
from axe_portfolio.util import axe_root


def main() -> None:
    load_dotenv(axe_root() / ".env", override=False)
    tracer = Tracer(agent="axe_portfolio")
    tracer.start()
    tracer.event(step="load_inputs", thought="reading IBKR CSV + portfolio snapshot")

    try:
        artifacts = run_portfolio_review()
    except Exception as exc:
        exc_desc = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
        tracer.event(step="error", thought=f"review failed: {exc_desc}")
        tracer.finalize(status="failed", summary=f"review failed: {exc_desc}", artifact_written=None)
        # Force-exit: ib_async leaves non-daemon threads alive after a failed
        # connection that prevent normal Python exit.
        os._exit(1)

    n_positions = len(artifacts.position_table)
    tracer.event(
        step="review_complete",
        thought=f"normalized {n_positions} positions",
        io={"out": {"positions": n_positions}},
    )
    tracer.finalize(
        status="success",
        summary=f"portfolio review — {n_positions} positions",
        artifact_written="portfolio.json",
    )

    print(json.dumps({
        "normalized_csv_path": str(artifacts.normalized_csv_path),
        "weekly_review_path": str(artifacts.weekly_review_path),
        "position_table": artifacts.position_table,
        "unified_sector_allocation": artifacts.unified_sector_allocation,
        "spy_comparison": artifacts.spy_comparison,
        "hishtalmut_status": artifacts.hishtalmut_status,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
