# Axe Capital — Agent Ground Rules

## Directory Boundary Rule

| Location | Purpose |
|---|---|
| `projects/Axe-Capital/` | **Everything Axe Capital builds** — code, normalized data, reports, specs, plans, runbooks, decision logs, sources |
| `obsidian-vault/` (Vault) | **Robert's personal notes only** — human-written research, journal entries, reading notes |

**Never write agent output into the Obsidian vault.** This includes: normalized CSVs, JSON reports, Python scripts, generated markdown docs, snapshots, memos, or any file produced by an agent or pipeline run.

## Broker Data (Read-Only Inputs)

Raw broker exports live in the Obsidian vault under Robert's control:
- IBKR statements → `Finance/raw/IBKR/Statements/`
- Portfolio snapshots → `Finance/raw/Portfolio/`

The agent reads them via read-only symlinks at:
```
projects/Axe-Capital/dashboard/data/raw/
  activity.csv           → Finance/raw/IBKR/Statements/Activity.csv
  statement.csv          → Finance/raw/IBKR/Statements/Statement.csv
  mtm_summary.csv        → Finance/raw/IBKR/Statements/MULTI_20260410.csv
  portfolio-current.csv  → Finance/raw/Portfolio/portfolio-current.csv
  portfolio-current-10-April.xlsx → Finance/raw/Portfolio/portfolio-current-10-April.xlsx
```

When Robert drops a new export into the vault, update the symlink (or add a new one) here. Never copy the raw file into the project directory.

## Project Structure

```
projects/Axe-Capital/
  dashboard/              # Dashboard views and normalized data outputs
    data/
      raw/               # Symlinks to vault broker exports (read-only)
      *.csv              # Normalized agent outputs
      normalize.py       # Data pipeline script
      manifest.json      # Data source manifest
    views/               # Rendered portfolio views
  spec/                  # Vision, strategy, architecture, org, risk docs
  plans/                 # Implementation plans, roadmaps, weekly cycles
  runbooks/              # Operational runbooks for agent workflows
  decision-log/          # Investment and architecture decision records
  sources/               # Research memos and source documents
  reports/               # Weekly review and ad-hoc report outputs
  step1-data-foundation/ # COO data pipeline package (axe_coo)
  step4-alpha-hunter/    # Alpha scanning package (axe_alpha)
  step5-portfolio-tracking/ # Portfolio tracker package (axe_portfolio)
```
