# 🧭 Master Categorized Tasks

Single consolidated task list, categorized and maintained for the whole vault.

## 🔗 Sources
- [[_raw/Tasks/Inbox]] (intake)
- [[Axe_Capital_Tasks]] (Axe Capital source list)

---

## 📥 Inbox (triage pending)
- [ ] (Jinx) Set up MinMax API key for `minimaxai/minimax-m2.7` so we stop falling back to GPT-5.2.
- [ ] (Jinx) Ingest all pending sources from `/_raw/` and move originals into the correct `Domain/raw/`.
- [ ] (Robert) Check MiniMax 2.7 API (working or not)

---

## ⚡️ OpenClaw / Ops
- [ ] Add MinMax (minimaxai) API key/auth to OpenClaw gateway so `minimaxai/minimax-m2.7` actually works (current behavior: missing minimaxai auth → fallback to `openai-codex/gpt-5.2`).
- [ ] Add Telegram alert whenever model fallback happens (especially when primary `minimaxai/minimax-m2.7` fails), include errorPreview/reason.
- [ ] Create a new session using main agent (context: openclaw-control-ui request, deadline: when convenient)

---

## 🪓 Axe Capital

### 🐛 Bug Fixes
- [ ] Portfolio cost basis and portfolio market value — remove percentage symbol, plus sign, and leading double zeros after decimal
- [ ] Internal dialogue viewer — not showing any outputs
- [ ] Portfolio state — legend not showing on red/yellow/green states; format status column better
- [ ] Refresh method on all panels — not working 🔺

---

### 🎨 Design
- [ ] Improve overall design and visual consistency — unified spacing, typography, color usage
- [ ] Add charts and graph views — P&L over time, position weights, alpha score distribution
- [ ] Add sector allocation pie chart — percentage per sector for concentration risk

---

### ⚙️ Implementation

#### 🧾 Weekly Review Pane
- [ ] What is the time horizon of the P&L displayed and what is the time horizon of the S&P comparison there
- [ ] Second IBKR account isn't aggregated there
- [ ] Parse the raw facts to a formatted fitting text

#### 🚀 Phase 2 — Make It Boot Like an App
- [ ] Write startup guide — `RUNNING.md` or AGENTS.md section
- [ ] Add scheduled portfolio refresh — every 15 min during market hours (09:30–16:00 ET)
- [ ] Add scheduled news and alpha refresh — daily schedule

#### ✨ Phase 4 — Dashboard Polish
- [ ] Add table column sorting and filtering — portfolio, decision archive, alpha panels
- [ ] Add social media / X feed integration — pull X posts for portfolio holdings

#### 🛡️ Phase 5 — Risk Infrastructure
- [ ] Add daily risk snapshot panel — 08:30 risk + positioning snapshot
- [ ] Wire risk limits into decision agent — hard-block violations
- [ ] Add post-trade monitoring module — track thesis progress after position entry

#### 🏛️ Phase 6 — Advanced / Governance
- [ ] Auto-generate IC Packet from decision output — PDF or markdown
- [ ] Add Portfolio Manager agent — portfolio construction (concentration, diversification, factor tilts)
- [ ] Set up systemd services for always-on operation
- [ ] Add weekly cadence automation — portfolio review, risk deep dive, research pipeline status

---

### 🔬 Research
- [ ] Check the stock market pro skill inside OpenClaw to integrate it with the dashboard
- [ ] Check what is coding-agent, tmux and taskflow skill in OpenClaw

---

### 📄 Documentation
- [ ] Fill in Risk Charter numeric limits — `spec/Risk/Risk_Charter_Draft.md` (max drawdown, concentration, sector exposure, liquidity floors)
- [ ] Document and configure Tailscale deployment — WSL on trading machine vs. separate Linux host

---

### 🖥️ UI / Observability
- [ ] Implement agent "windows" a window to see the agents running their tasks (analyzing, auditing, internal logic, dialouges, task status) 🔺
- [ ] Name agents and make 1 responsible for each pane, have a list somewhere easily accesiable to view details. 🔺
