from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv
from axe_core import Tracer
from axe_portfolio.tracker import run_portfolio_review
from axe_portfolio.util import axe_root

logging.basicConfig(
    level=logging.WARNING,
    format="  [%(levelname)s] %(message)s",
)

_SOURCE_LABEL = {
    "ibkr": "IBKR live",
    "flex": "Flex Query (T+1)",
    "normalized": "cached CSV (stale)",
    "raw": "raw CSV (stale)",
}


def main(force_exit_on_failure: bool = False) -> int:
    load_dotenv(axe_root() / ".env", override=False)
    tracer = Tracer(agent="axe_portfolio")
    tracer.start()
    tracer.event(step="load_inputs", thought="resolving portfolio source (IBKR live → Flex Query → cached CSV)")

    try:
        artifacts = run_portfolio_review()
    except Exception as exc:
        exc_desc = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
        tracer.event(step="error", thought=f"review failed: {exc_desc}")
        tracer.finalize(status="failed", summary=f"review failed: {exc_desc}", artifact_written=None)
        if force_exit_on_failure:
            # Force-exit for the script entry path: ib_async can leave
            # non-daemon threads alive after a failed connection attempt.
            os._exit(1)
        raise

    n_positions = len(artifacts.position_table)
    source_label = _SOURCE_LABEL.get(artifacts.data_source, artifacts.data_source)
    tracer.event(
        step="review_complete",
        thought=f"{source_label} — {n_positions} positions",
        io={"out": {"positions": n_positions, "data_source": artifacts.data_source}},
    )
    tracer.finalize(
        status="success",
        summary=f"portfolio review — {n_positions} positions ({source_label})",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main(force_exit_on_failure=True))
