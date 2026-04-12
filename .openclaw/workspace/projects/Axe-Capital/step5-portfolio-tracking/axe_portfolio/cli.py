from __future__ import annotations

import json

from axe_portfolio.tracker import run_portfolio_review


def main() -> None:
    artifacts = run_portfolio_review()
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
