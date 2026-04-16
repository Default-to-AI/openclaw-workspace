# Opportunity To Memo Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the outside-portfolio opportunity-to-memo pipeline and local reboot-surviving service setup.

**Architecture:** Reuse Step 4 alpha scanning, Step 8/9/10 specialists, and Step 3 decisions. Step 7 becomes the orchestration layer for `opportunities`, while Step 3 adds explicit Risk Manager and Compliance/Audit stages. Production setup is delivered as user-systemd unit templates plus an installer script under `ops/`.

**Tech Stack:** Python 3.11, pytest, FastAPI/uvicorn, Vite/npm, yfinance/OpenAI in existing agents, user systemd on Linux.

---

### Task 1: Live Portfolio Exclusion In Alpha Hunter

**Files:**
- Modify: `step4-alpha-hunter/axe_alpha/alpha_scan.py`
- Modify: `step4-alpha-hunter/tests/test_cli_trace.py`

- [ ] Add tests for loading held symbols from `portfolio.json` and filtering alpha candidates.
- [ ] Implement `load_live_held_symbols()` and use it in `run_alpha_hunter_scan`.
- [ ] Verify `step4-alpha-hunter` tests pass.

### Task 2: Opportunity Pipeline Runner

**Files:**
- Modify: `step7-automation/axe_orchestrator/runners.py`
- Modify: `step7-automation/axe_orchestrator/cli.py`
- Modify: `step7-automation/axe_orchestrator/api.py`
- Modify: `step7-automation/tests/test_cli.py`
- Modify: `step7-automation/tests/test_api.py`

- [ ] Add tests for candidate selection and `run_opportunities`.
- [ ] Implement `opportunity_tickers(limit=2)` from `alpha-latest.json`.
- [ ] Implement `run_opportunities(limit=None)` to run portfolio, alpha, specialists, then decisions.
- [ ] Add CLI/API target `opportunities`.
- [ ] Verify Step 7 tests pass.

### Task 3: Risk Manager And Compliance Decision Chain

**Files:**
- Modify: `step3-debate-decision/axe_decision/cli.py`
- Modify: `step3-debate-decision/tests/test_analyst_reports.py`

- [ ] Add tests for decision artifact structure.
- [ ] Add Risk Manager prompt and Compliance/Audit prompt.
- [ ] Feed risk/compliance into CEO.
- [ ] Keep `cro` alias for dashboard compatibility.
- [ ] Verify Step 3 tests pass.

### Task 4: Production Service Setup

**Files:**
- Create: `ops/systemd/axe-api.service`
- Create: `ops/systemd/axe-dashboard.service`
- Create: `ops/systemd/axe-monthly-specialists.service`
- Create: `ops/systemd/axe-monthly-specialists.timer`
- Create: `ops/install_user_services.sh`
- Modify: `runbooks/prototype-launch.md`
- Modify: `_INDEX.md`

- [ ] Add user-systemd unit files.
- [ ] Add installer script.
- [ ] Document install/start/status commands.
- [ ] Verify service files are syntactically inspectable and shell script parses.

### Task 5: Full Verification

Run:

```bash
cd ~/.openclaw/workspace/projects/Axe-Capital/step4-alpha-hunter && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step7-automation && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step3-debate-decision && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step8-fundamental && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step9-technical && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step10-macro && pytest -q
cd ~/.openclaw/workspace/projects/Axe-Capital/step6-dashboard && npm run build
bash -n ~/.openclaw/workspace/projects/Axe-Capital/ops/install_user_services.sh
```

