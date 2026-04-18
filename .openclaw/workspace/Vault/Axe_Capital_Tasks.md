# Axe Capital — Master To-Do (Categorized)

Organized by category: Implementation, Design, Bug Fix, Research, Documentation.

---

## 🐛 Bug Fixes

- [ ] Portfolio cost basis and portfolio market value — remove percentage symbol, plus sign, and leading double zeros after decimal
- [ ] Internal dialogue viewer — not showing any outputs
- [ ] Portfolio state — legend not showing on red/yellow/green states; format status column better
- [x] Panel 3 — remove "panel 3" string from title; fix inconsistent date format (2026-04-16T04:20:50.264435+03:00)
- [ ] Refresh method on all panels — not working 🔺
- [x] Date and timestamp display — standardize formats across panels (Phase 4)

---

## 🎨 Design

- [x] Panel 5 and 6 — make consistent, remove panel numbering, just show names (Agent Status Board, Internal Dialogue Viewer)
- [ ] Improve overall design and visual consistency — unified spacing, typography, color usage
- [ ] Add charts and graph views — P&L over time, position weights, alpha score distribution
- [ ] Add sector allocation pie chart — percentage per sector for concentration risk

---

## ⚙️ Implementation

### Weekly Review Pane
- [ ] What is the time horizon of the P&L displayed and what is the time horizon of the S&P comparison there
- [ ] Second IBKR account isn't aggregated there
- [ ] Parse the raw facts to a formatted fitting text

### Phase 2 — Make It Boot Like an App
- [ ] Write startup guide — `RUNNING.md` or AGENTS.md section
- [ ] Add scheduled portfolio refresh — every 15 min during market hours (09:30–16:00 ET)
- [ ] Add scheduled news and alpha refresh — daily schedule

### Phase 3 — Close the Decision Workflow Loop
- [x] Add Approval Queue panel to dashboard — render `approval-queue.md` (Pending/Approved/Executed tables)

### Phase 4 — Dashboard Polish
- [ ] Add table column sorting and filtering — portfolio, decision archive, alpha panels
- [ ] Add social media / X feed integration — pull X posts for portfolio holdings

### Phase 5 — Risk Infrastructure
- [ ] Add daily risk snapshot panel — 08:30 risk + positioning snapshot
- [ ] Wire risk limits into decision agent — hard-block violations
- [ ] Add post-trade monitoring module — track thesis progress after position entry

### Phase 6 — Advanced / Governance
- [ ] Auto-generate IC Packet from decision output — PDF or markdown
- [ ] Add Portfolio Manager agent — portfolio construction (concentration, diversification, factor tilts)
- [ ] Set up systemd services for always-on operation
- [ ] Add weekly cadence automation — portfolio review, risk deep dive, research pipeline status

---

## 🔬 Research

- [ ] Check the stock market pro skill inside OpenClaw to integrate it with the dashboard
- [ ] Check what is coding-agent, tmux and taskflow skill in OpenClaw

---

## 📄 Documentation

### Phase 5 — Risk Infrastructure
- [ ] Fill in Risk Charter numeric limits — `spec/Risk/Risk_Charter_Draft.md` (max drawdown, concentration, sector exposure, liquidity floors)

### Phase 6 — Advanced / Governance
- [ ] Document and configure Tailscale deployment — WSL on trading machine vs. separate Linux host

---
- [ ] Implement agent "windows" a window to see the agents running their tasks (analyzing, auditing, internal logic, dialouges, task status) 🔺 
- [ ] Name agents and make 1 responsible for each pane, have a list somewhere easily accesiable to view details.🔺 
## ✅ Completed

### Phase 1 — Make Existing Output Visible
- [x] Add Decision Report panel to dashboard
- [x] Add Analyst Reports panel to dashboard
- [x] Wire CEO decision output → Approval Queue
- [x] Remove orphaned dashboard components

### Phase 2 — Make It Boot Like an App
- [x] Create `./scripts/dev.sh`
- [x] Create `./scripts/refresh.sh`

### Phase 3 — Close the Decision Workflow Loop
- [x] Auto-run decision after specialists
- [x] Add Weekly Review panel
- [x] Add decision archive pruning