# Axe Capital — Agent Ground Rules

## Directory Boundary Rule

| Location | Purpose |
|---|---|
| `projects/Axe-Capital/` | **Everything Axe Capital builds** — code, normalized data, reports, specs, plans, runbooks, decision logs, sources |
| `obsidian-vault/` (Vault) | **Robert's personal notes only** — human-written research, journal entries, reading notes |

**Never write agent output into the Obsidian vault.** This includes: normalized CSVs, JSON reports, Python scripts, generated markdown docs, snapshots, memos, or any file produced by an agent or pipeline run.

## Broker Data (Read-Only Inputs)

The system pulls live portfolio data directly from IBKR API. Historical exports can be stored in the vault:
- IBKR statements → `Finance/raw/IBKR/Statements/`
- Portfolio snapshots → `Finance/raw/Portfolio/`

The system reads portfolio data via `.env` configured IBKR gateway connection.

## Project Structure

```
projects/Axe-Capital/
  step0-shared/            # axe_core shared package
  step1-data-foundation/   # axe_coo data pipeline
  step2-news/              # axe_news RSS + LLM scorer
  step3-debate-decision/   # axe_decision debate layer
  step4-alpha-hunter/      # axe_alpha alpha scanner
  step5-portfolio-tracking/ # axe_portfolio tracker
  step6-dashboard/        # Dashboard UI (artifact home: public/)
    public/               # All artifacts (portfolio.json, alpha-latest.json, analyst-reports/, etc.)
  step7-automation/       # axe_orchestrator CLI + FastAPI
  step8-fundamental/     # axe_fundamental analyst
  step9-technical/       # axe_technical analyst
  step10-macro/          # axe_macro strategist
  spec/                  # Vision, strategy, architecture, org, risk docs
  plans/                 # Implementation plans, roadmaps
  runbooks/              # Operational runbooks for agent workflows
  ops/                   # systemd services, install scripts
```

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health
