# Axe Dashboard data

Current source of truth for portfolio data is `dashboard/data/`.

## Supported inputs

The portfolio tracker now auto-detects inputs in this order:
1. `portfolio_latest.normalized.csv` (preferred)
2. raw portfolio CSV files such as:
   - `raw/portfolio-current.csv`
   - `raw/portfolio_current.csv`
   - `portfolio-current.csv`
   - `portfolio_current.csv`

## Preferred filenames
- `portfolio_latest.normalized.csv`
- `activity_kv.latest.csv`
- `realized_kv.latest.csv`
- `mtm_kv.latest.csv`

Raw files may exist, but they are no longer mandatory for the Step 5 pipeline to run.
