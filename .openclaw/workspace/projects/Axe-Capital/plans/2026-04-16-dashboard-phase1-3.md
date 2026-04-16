# Axe Capital Dashboard — Phase 1–3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all generated agent output visible in the dashboard, close the approval-queue loop, add boot scripts, and wire specialist chains.

**Architecture:** File-first: all new panels read from `step6-dashboard/public/` artifacts. No new API routes needed. Approval-queue write happens inside the decision CLI (step3) so it runs whether triggered from API or CLI. Scripts are plain bash, no new dependencies.

**Tech Stack:** React + Vite + Tailwind (dashboard), Python (step3 decision CLI, step7 runners), bash (scripts)

---

## File Map

**Create:**
- `step6-dashboard/src/components/DecisionReportPanel.jsx` — renders `decision-latest.json`
- `step6-dashboard/src/components/AnalystReportsPanel.jsx` — renders `analyst-reports/index.json` + per-ticker reports
- `step6-dashboard/src/components/WeeklyReviewPanel.jsx` — renders `weekly-review-latest.json`
- `scripts/dev.sh` — start API + dashboard in one command
- `scripts/refresh.sh` — wrapper around `axe run`

**Modify:**
- `step6-dashboard/src/App.jsx` — add new panels, remove orphaned imports
- `step3-debate-decision/axe_decision/cli.py` — add `_update_approval_queue()` call after CEO decision
- `step7-automation/axe_orchestrator/runners.py` — auto-chain decision after specialists

**Delete:**
- `step6-dashboard/src/components/DecisionLogPanel.jsx` — orphaned, never mounted, superseded by DecisionArchivePanel
- `step6-dashboard/src/components/RunbookPanel.jsx` — orphaned, hardcoded dead localhost URLs

---

## Task 1: Delete orphaned components

**Files:**
- Delete: `step6-dashboard/src/components/DecisionLogPanel.jsx`
- Delete: `step6-dashboard/src/components/RunbookPanel.jsx`

- [ ] **Step 1: Confirm neither is imported in App.jsx**

```bash
grep -n "DecisionLogPanel\|RunbookPanel" step6-dashboard/src/App.jsx
```
Expected: no output (they are not imported)

- [ ] **Step 2: Delete both files**

```bash
rm step6-dashboard/src/components/DecisionLogPanel.jsx
rm step6-dashboard/src/components/RunbookPanel.jsx
```

- [ ] **Step 3: Confirm dashboard still builds**

```bash
cd step6-dashboard && npm run build 2>&1 | tail -5
```
Expected: build succeeds, no errors about missing files

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "chore: remove orphaned DecisionLogPanel and RunbookPanel components"
```

---

## Task 2: DecisionReportPanel — the full CEO memo

**Files:**
- Create: `step6-dashboard/src/components/DecisionReportPanel.jsx`
- Modify: `step6-dashboard/src/App.jsx`

The `decision-latest.json` shape:
```
{ ticker, generated_at,
  bull: { thesis, catalysts[], valuation, technicals, risks_acknowledged[], confidence_1_to_10, sources_used[] },
  bear: { thesis, kill_shots[], downside_scenarios[], invalidation_levels[], risks[], confidence_1_to_10 },
  risk_manager: { gate, veto_rationale, scenario_risks[], required_conditions[], suggested_stop_loss_pct, suggested_position_size_pct, concentration_notes },
  compliance: { audit_status, source_coverage, missing_evidence[], assumption_quality, manual_approval_required, audit_notes },
  ceo: { action, conviction_1_to_10, thesis, entry_zone, profit_target, stop_loss, position_size_pct, bear_case, rationale, data_gaps }
}
```

- [ ] **Step 1: Create DecisionReportPanel.jsx**

Create `step6-dashboard/src/components/DecisionReportPanel.jsx` with this content:

```jsx
import { useEffect, useState } from 'react'
import { fetchJsonWithFallback } from '../lib/api'

function actionTone(action) {
  if (action === 'BUY') return 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
  if (action === 'SELL') return 'text-red-300 border-red-700/60 bg-red-900/10'
  if (action === 'HOLD') return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  return 'text-axe-dim border-axe-border bg-axe-muted/20'
}

function gateTone(gate) {
  if (gate === 'APPROVED') return 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
  if (gate === 'CONDITIONAL') return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  if (gate === 'BLOCKED') return 'text-red-300 border-red-700/60 bg-red-900/10'
  return 'text-axe-dim border-axe-border bg-axe-muted/20'
}

function auditTone(status) {
  if (status === 'PASS') return 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
  if (status === 'NEEDS_MORE_EVIDENCE') return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  if (status === 'FAIL') return 'text-red-300 border-red-700/60 bg-red-900/10'
  return 'text-axe-dim border-axe-border bg-axe-muted/20'
}

function convictionTone(score) {
  if (score >= 8) return 'text-emerald-300'
  if (score >= 5) return 'text-amber-300'
  return 'text-red-300'
}

function Section({ title, badge, badgeTone, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border border-axe-border rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-3 bg-axe-bg/40 hover:bg-white/[0.02] text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-center gap-2">
          <span className="text-axe-text text-sm font-medium">{title}</span>
          {badge && (
            <span className={`ui-badge ${badgeTone}`}>{badge}</span>
          )}
        </div>
        <span className="text-axe-dim text-xs">{open ? 'hide' : 'show'}</span>
      </button>
      {open && <div className="px-4 py-4 space-y-3">{children}</div>}
    </div>
  )
}

function ListItems({ items }) {
  if (!items || items.length === 0) return <span className="text-axe-dim text-xs">—</span>
  return (
    <ul className="space-y-1">
      {items.map((item, i) => (
        <li key={i} className="text-xs text-axe-dim flex gap-2">
          <span className="text-axe-accent shrink-0">·</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  )
}

function Field({ label, value, valueClass = 'text-axe-text' }) {
  if (!value && value !== 0) return null
  return (
    <div>
      <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-sm ${valueClass}`}>{value}</div>
    </div>
  )
}

export default function DecisionReportPanel({ refreshToken }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setData(null)
    setError(null)
    fetchJsonWithFallback({ filePath: '/decision-latest.json' })
      .then((payload) => {
        if (cancelled) return
        setData(payload)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
      })
    return () => { cancelled = true }
  }, [refreshToken])

  const ceo = data?.ceo || {}
  const bull = data?.bull || {}
  const bear = data?.bear || {}
  const rm = data?.risk_manager || {}
  const compliance = data?.compliance || {}

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="panel-title">Decision Memo</div>
          <p className="text-axe-dim text-xs mt-1">
            Latest CEO decision · bull · bear · risk gate · compliance
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {data && (
            <>
              <span className="text-axe-dim">{data.ticker}</span>
              <span className={`ui-badge ${actionTone(ceo.action)}`}>{ceo.action || '—'}</span>
              <span className={`ui-badge ${convictionTone(ceo.conviction_1_to_10)} border-axe-border`}>
                conviction {ceo.conviction_1_to_10 ?? '—'}/10
              </span>
              <span className="text-axe-dim">{data.generated_at}</span>
            </>
          )}
        </div>
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load decision: {error}</div>}
      {!data && !error && <div className="mt-4 text-sm text-axe-dim">Loading decision memo…</div>}

      {data && (
        <div className="space-y-3 mt-4">
          {/* CEO Summary — always open */}
          <Section
            title="CEO Decision"
            badge={ceo.action || '—'}
            badgeTone={actionTone(ceo.action)}
            defaultOpen={true}
          >
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
              <div className="stat-card">
                <div className="text-axe-dim text-xs uppercase tracking-wider">Entry Zone</div>
                <div className="text-axe-text text-sm font-semibold mt-1">{ceo.entry_zone ?? '—'}</div>
              </div>
              <div className="stat-card">
                <div className="text-axe-dim text-xs uppercase tracking-wider">Target</div>
                <div className="text-axe-text text-sm font-semibold mt-1">{ceo.profit_target ?? '—'}</div>
              </div>
              <div className="stat-card">
                <div className="text-axe-dim text-xs uppercase tracking-wider">Stop Loss</div>
                <div className="text-axe-text text-sm font-semibold mt-1">{ceo.stop_loss ?? '—'}</div>
              </div>
              <div className="stat-card">
                <div className="text-axe-dim text-xs uppercase tracking-wider">Size</div>
                <div className="text-axe-text text-sm font-semibold mt-1">
                  {ceo.position_size_pct != null ? `${ceo.position_size_pct}%` : '—'}
                </div>
              </div>
            </div>
            <Field label="Thesis" value={ceo.thesis} />
            <Field label="Rationale" value={ceo.rationale} />
            {ceo.bear_case && <Field label="Bear case acknowledged" value={ceo.bear_case} valueClass="text-red-200" />}
            {ceo.data_gaps && <Field label="Data gaps" value={ceo.data_gaps} valueClass="text-amber-300" />}
          </Section>

          {/* Risk Gate */}
          <Section
            title="Risk Manager"
            badge={rm.gate || '—'}
            badgeTone={gateTone(rm.gate)}
          >
            {rm.veto_rationale && <Field label="Veto rationale" value={rm.veto_rationale} valueClass="text-red-200" />}
            {rm.required_conditions?.length > 0 && (
              <div>
                <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">Required conditions</div>
                <ListItems items={rm.required_conditions} />
              </div>
            )}
            <div className="grid grid-cols-2 gap-3">
              <div className="stat-card">
                <div className="text-axe-dim text-xs uppercase tracking-wider">Suggested stop</div>
                <div className="text-axe-text text-sm font-semibold mt-1">
                  {rm.suggested_stop_loss_pct != null ? `${rm.suggested_stop_loss_pct}%` : '—'}
                </div>
              </div>
              <div className="stat-card">
                <div className="text-axe-dim text-xs uppercase tracking-wider">Suggested size</div>
                <div className="text-axe-text text-sm font-semibold mt-1">
                  {rm.suggested_position_size_pct != null ? `${rm.suggested_position_size_pct}%` : '—'}
                </div>
              </div>
            </div>
            {rm.concentration_notes && <Field label="Concentration" value={rm.concentration_notes} valueClass="text-amber-300" />}
            {rm.scenario_risks?.length > 0 && (
              <div>
                <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">Scenario risks</div>
                <ListItems items={rm.scenario_risks} />
              </div>
            )}
          </Section>

          {/* Compliance */}
          <Section
            title="Compliance / Audit"
            badge={compliance.audit_status || '—'}
            badgeTone={auditTone(compliance.audit_status)}
          >
            <Field label="Audit notes" value={compliance.audit_notes} />
            {compliance.missing_evidence?.length > 0 && (
              <div>
                <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">Missing evidence</div>
                <ListItems items={compliance.missing_evidence} />
              </div>
            )}
            {compliance.manual_approval_required && (
              <span className="ui-badge text-amber-300 border-amber-700/60 bg-amber-900/10">manual approval required</span>
            )}
          </Section>

          {/* Bull */}
          <Section
            title="Bull Case"
            badge={bull.confidence_1_to_10 != null ? `confidence ${bull.confidence_1_to_10}/10` : undefined}
            badgeTone="text-emerald-300 border-emerald-700/60 bg-emerald-900/10"
          >
            <Field label="Thesis" value={bull.thesis} />
            <Field label="Valuation" value={bull.valuation} />
            <Field label="Technicals" value={bull.technicals} />
            {bull.catalysts?.length > 0 && (
              <div>
                <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">Catalysts</div>
                <ListItems items={bull.catalysts} />
              </div>
            )}
            {bull.risks_acknowledged?.length > 0 && (
              <div>
                <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">Risks acknowledged</div>
                <ListItems items={bull.risks_acknowledged} />
              </div>
            )}
          </Section>

          {/* Bear */}
          <Section
            title="Bear Case"
            badge={bear.confidence_1_to_10 != null ? `confidence ${bear.confidence_1_to_10}/10` : undefined}
            badgeTone="text-red-300 border-red-700/60 bg-red-900/10"
          >
            <Field label="Thesis" value={bear.thesis} valueClass="text-red-200" />
            {bear.kill_shots?.length > 0 && (
              <div>
                <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">Kill shots</div>
                <ListItems items={bear.kill_shots} />
              </div>
            )}
            {bear.downside_scenarios?.length > 0 && (
              <div>
                <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">Downside scenarios</div>
                <ListItems items={bear.downside_scenarios} />
              </div>
            )}
            {bear.invalidation_levels?.length > 0 && (
              <div>
                <div className="text-axe-dim text-xs uppercase tracking-wider mb-1">Invalidation levels</div>
                <ListItems items={bear.invalidation_levels} />
              </div>
            )}
          </Section>
        </div>
      )}
    </section>
  )
}
```

- [ ] **Step 2: Add DecisionReportPanel to App.jsx**

In `step6-dashboard/src/App.jsx`, add the import after the existing imports:
```jsx
import DecisionReportPanel from './components/DecisionReportPanel'
```

Then add the panel just before `<DecisionArchivePanel .../>`:
```jsx
        <DecisionReportPanel key={`decision-report-${refreshToken}`} refreshToken={refreshToken} />
```

- [ ] **Step 3: Verify build**

```bash
cd step6-dashboard && npm run build 2>&1 | tail -8
```
Expected: build succeeds with no errors

- [ ] **Step 4: Commit**

```bash
git add step6-dashboard/src/components/DecisionReportPanel.jsx step6-dashboard/src/App.jsx
git commit -m "feat(dashboard): add DecisionReportPanel — renders CEO decision, risk gate, compliance, bull/bear"
```

---

## Task 3: AnalystReportsPanel — per-ticker fundamental/technical/macro

**Files:**
- Create: `step6-dashboard/src/components/AnalystReportsPanel.jsx`
- Modify: `step6-dashboard/src/App.jsx`

The `analyst-reports/index.json` shape:
```json
{ "generated_at": "...", "symbols": { "PFE": { "fundamental": { "json_path": "...", "updated_at": "..." }, "technical": {...}, "macro": {...} } } }
```

Each report JSON shape: `{ ticker, agent, summary, key_findings, report, metrics, confidence, data_sources }`

- [ ] **Step 1: Create AnalystReportsPanel.jsx**

Create `step6-dashboard/src/components/AnalystReportsPanel.jsx`:

```jsx
import { useEffect, useState } from 'react'
import { fetchJsonWithFallback } from '../lib/api'

const AGENT_LABELS = {
  fundamental: 'Fundamental',
  technical: 'Technical',
  macro: 'Macro',
}

function ReportView({ report }) {
  if (!report) return <div className="text-axe-dim text-xs">No report loaded.</div>

  const findings = report.key_findings || {}

  return (
    <div className="space-y-4">
      {report.summary && (
        <p className="text-sm text-axe-text leading-6">{report.summary}</p>
      )}

      {report.confidence && (
        <div className="flex items-center gap-2">
          <span className="text-axe-dim text-xs uppercase tracking-wider">Confidence</span>
          <span className="ui-badge text-axe-dim border-axe-border bg-axe-muted/20">{report.confidence}</span>
        </div>
      )}

      {Object.keys(findings).length > 0 && (
        <div>
          <div className="text-axe-dim text-xs uppercase tracking-wider mb-2">Key Findings</div>
          <div className="space-y-2">
            {Object.entries(findings).map(([k, v]) => (
              <div key={k} className="text-xs">
                <span className="text-axe-dim">{k}: </span>
                <span className="text-axe-text">
                  {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {report.report && (
        <div>
          <div className="text-axe-dim text-xs uppercase tracking-wider mb-2">Full Report</div>
          <p className="text-xs text-axe-dim leading-5 whitespace-pre-wrap">{report.report}</p>
        </div>
      )}

      {report.data_sources?.length > 0 && (
        <div className="text-axe-dim text-xs">
          Sources: {report.data_sources.join(', ')}
        </div>
      )}
    </div>
  )
}

export default function AnalystReportsPanel({ refreshToken }) {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState(null)
  const [selectedSymbol, setSelectedSymbol] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState('fundamental')
  const [report, setReport] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [reportError, setReportError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setIndex(null)
    setError(null)
    fetchJsonWithFallback({ filePath: '/analyst-reports/index.json' })
      .then((payload) => {
        if (cancelled) return
        setIndex(payload)
        const symbols = Object.keys(payload.symbols || {})
        if (symbols.length > 0) setSelectedSymbol(symbols[0])
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
      })
    return () => { cancelled = true }
  }, [refreshToken])

  useEffect(() => {
    if (!index || !selectedSymbol) return
    const meta = index.symbols?.[selectedSymbol]?.[selectedAgent]
    if (!meta?.json_path) { setReport(null); return }

    let cancelled = false
    setReportLoading(true)
    setReportError(null)
    setReport(null)
    fetchJsonWithFallback({ filePath: `/analyst-reports/${meta.json_path}` })
      .then((payload) => {
        if (cancelled) return
        setReport(payload)
        setReportLoading(false)
      })
      .catch((err) => {
        if (cancelled) return
        setReportError(err.message)
        setReportLoading(false)
      })
    return () => { cancelled = true }
  }, [index, selectedSymbol, selectedAgent])

  const symbols = Object.keys(index?.symbols || {})

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="panel-title">Analyst Reports</div>
          <p className="text-axe-dim text-xs mt-1">
            Per-ticker fundamental · technical · macro from specialist agents
          </p>
        </div>
        <div className="text-axe-dim text-xs">
          {index ? `${symbols.length} symbol${symbols.length !== 1 ? 's' : ''} · ${index.generated_at || ''}` : 'loading…'}
        </div>
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load analyst index: {error}</div>}

      {!error && index && (
        <div className="mt-4 space-y-4">
          {/* Controls */}
          <div className="flex flex-wrap gap-2">
            {symbols.map((sym) => (
              <button
                key={sym}
                className={selectedSymbol === sym ? 'ui-button' : 'ui-button-secondary'}
                onClick={() => setSelectedSymbol(sym)}
              >
                {sym}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            {Object.entries(AGENT_LABELS).map(([agent, label]) => {
              const hasMeta = !!index.symbols?.[selectedSymbol]?.[agent]
              return (
                <button
                  key={agent}
                  className={selectedAgent === agent ? 'ui-button' : 'ui-button-secondary'}
                  onClick={() => setSelectedAgent(agent)}
                  disabled={!hasMeta}
                >
                  {label}
                  {!hasMeta && ' (—)'}
                </button>
              )
            })}
          </div>

          {/* Report area */}
          <div className="bg-axe-bg/30 border border-axe-border rounded-lg p-4">
            {reportLoading && <div className="text-sm text-axe-dim">Loading {selectedAgent} report for {selectedSymbol}…</div>}
            {reportError && <div className="text-sm text-red-300">Failed to load report: {reportError}</div>}
            {!reportLoading && !reportError && <ReportView report={report} />}
          </div>
        </div>
      )}

      {!error && !index && !error && (
        <div className="mt-4 text-sm text-axe-dim">Loading analyst index…</div>
      )}
    </section>
  )
}
```

- [ ] **Step 2: Add AnalystReportsPanel to App.jsx**

Add import:
```jsx
import AnalystReportsPanel from './components/AnalystReportsPanel'
```

Add after `DecisionReportPanel`:
```jsx
        <AnalystReportsPanel key={`analyst-${refreshToken}`} refreshToken={refreshToken} />
```

- [ ] **Step 3: Verify build**

```bash
cd step6-dashboard && npm run build 2>&1 | tail -8
```

- [ ] **Step 4: Commit**

```bash
git add step6-dashboard/src/components/AnalystReportsPanel.jsx step6-dashboard/src/App.jsx
git commit -m "feat(dashboard): add AnalystReportsPanel — browse fundamental/technical/macro per symbol"
```

---

## Task 4: WeeklyReviewPanel — portfolio health snapshot

**Files:**
- Create: `step6-dashboard/src/components/WeeklyReviewPanel.jsx`
- Modify: `step6-dashboard/src/App.jsx`

The `weekly-review-latest.json` shape:
```json
{ "review_date": "...", "positions": [ { "symbol", "market_value", "unrealized_pl", "unrealized_pl_pct", "stop_loss_level", "distance_to_stop_pct", "alert_status", "sector_tag", "weight_pct" } ], "sector_concentration": {...}, "spy_comparison": {...}, "hishtalmut_status": {...} }
```

- [ ] **Step 1: Create WeeklyReviewPanel.jsx**

Create `step6-dashboard/src/components/WeeklyReviewPanel.jsx`:

```jsx
import { useEffect, useState } from 'react'
import { fetchJsonWithFallback } from '../lib/api'

const fmt = (n, digits = 2) =>
  n == null ? '—' : n.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits })

const sign = (n) => (n > 0 ? '+' : '')

const pnlClass = (n) => {
  if (n == null) return 'text-axe-dim'
  if (n > 0) return 'pnl-pos'
  if (n < 0) return 'pnl-neg'
  return 'pnl-flat'
}

function AlertBadge({ status }) {
  return <span className={`alert-pill alert-${status}`}>{status}</span>
}

export default function WeeklyReviewPanel({ refreshToken }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setData(null)
    setError(null)
    fetchJsonWithFallback({ filePath: '/weekly-review-latest.json' })
      .then((payload) => {
        if (cancelled) return
        setData(payload)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
      })
    return () => { cancelled = true }
  }, [refreshToken])

  const positions = data?.positions || []
  const redCount = positions.filter((p) => p.alert_status === 'RED').length
  const yellowCount = positions.filter((p) => p.alert_status === 'YELLOW').length

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="panel-title">Weekly Review</div>
          <p className="text-axe-dim text-xs mt-1">
            Latest portfolio health snapshot · {data?.review_date || '—'}
          </p>
        </div>
        {data && (
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="flex items-center gap-1.5 text-axe-red">
              <span className="w-2 h-2 rounded-sm bg-red-600" /> {redCount} RED
            </span>
            <span className="flex items-center gap-1.5 text-amber-400">
              <span className="w-2 h-2 rounded-sm bg-amber-500" /> {yellowCount} YELLOW
            </span>
          </div>
        )}
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load weekly review: {error}</div>}
      {!data && !error && <div className="mt-4 text-sm text-axe-dim">Loading weekly review…</div>}

      {data && (
        <div className="space-y-4 mt-4">
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="pl-4">Symbol</th>
                  <th>Sector</th>
                  <th>Mkt Value</th>
                  <th>UPL $</th>
                  <th>UPL %</th>
                  <th>Stop</th>
                  <th>Dist%</th>
                  <th>Wt%</th>
                  <th className="pr-4">Status</th>
                </tr>
              </thead>
              <tbody>
                {[...positions]
                  .sort((a, b) => {
                    const order = { RED: 0, YELLOW: 1, GREEN: 2 }
                    return (order[a.alert_status] ?? 3) - (order[b.alert_status] ?? 3)
                  })
                  .map((p) => (
                    <tr key={p.symbol}>
                      <td className="pl-4 font-semibold text-axe-text">{p.symbol}</td>
                      <td className="text-left text-axe-dim max-w-[120px] truncate">{p.sector_tag}</td>
                      <td>${fmt(p.market_value, 0)}</td>
                      <td className={pnlClass(p.unrealized_pl)}>
                        {p.unrealized_pl != null ? `${sign(p.unrealized_pl)}$${fmt(Math.abs(p.unrealized_pl), 0)}` : '—'}
                      </td>
                      <td className={`font-medium ${pnlClass(p.unrealized_pl_pct)}`}>
                        {p.unrealized_pl_pct != null ? `${sign(p.unrealized_pl_pct)}${fmt(p.unrealized_pl_pct)}%` : '—'}
                      </td>
                      <td className="text-axe-dim">${fmt(p.stop_loss_level)}</td>
                      <td className={p.distance_to_stop_pct != null && p.distance_to_stop_pct < 0 ? 'pnl-neg font-medium' : 'text-axe-dim'}>
                        {p.distance_to_stop_pct != null ? `${sign(p.distance_to_stop_pct)}${fmt(p.distance_to_stop_pct)}%` : '—'}
                      </td>
                      <td className="text-axe-dim">{fmt(p.weight_pct, 1)}%</td>
                      <td className="pr-4"><AlertBadge status={p.alert_status} /></td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {data.spy_comparison && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {Object.entries(data.spy_comparison).map(([k, v]) => (
                <div key={k} className="stat-card">
                  <div className="text-axe-dim text-xs uppercase tracking-wider">{k.replace(/_/g, ' ')}</div>
                  <div className="text-axe-text text-sm font-semibold mt-1">
                    {typeof v === 'number' ? `${sign(v)}${fmt(v)}%` : String(v)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  )
}
```

- [ ] **Step 2: Add WeeklyReviewPanel to App.jsx**

Add import:
```jsx
import WeeklyReviewPanel from './components/WeeklyReviewPanel'
```

Add after `AnalystReportsPanel`:
```jsx
        <WeeklyReviewPanel key={`weekly-${refreshToken}`} refreshToken={refreshToken} />
```

- [ ] **Step 3: Verify build**

```bash
cd step6-dashboard && npm run build 2>&1 | tail -8
```

- [ ] **Step 4: Commit**

```bash
git add step6-dashboard/src/components/WeeklyReviewPanel.jsx step6-dashboard/src/App.jsx
git commit -m "feat(dashboard): add WeeklyReviewPanel — portfolio health snapshot from weekly-review-latest.json"
```

---

## Task 5: Wire CEO decision → Approval Queue

**Files:**
- Modify: `step3-debate-decision/axe_decision/cli.py`

When CEO action is `BUY`, `SELL`, or `HOLD` (not `PASS`), append a formatted row to `public/approval-queue.md` under `## Pending approvals`.

- [ ] **Step 1: Add `_update_approval_queue` function to cli.py**

In `step3-debate-decision/axe_decision/cli.py`, add this function after `_append_jsonl`:

```python
def _update_approval_queue(pub: Path, ticker: str, ceo: dict, generated_at: str) -> None:
    """Append actionable CEO decisions to approval-queue.md pending table."""
    action = ceo.get("action", "PASS")
    if action == "PASS":
        return  # PASS decisions don't go to the approval queue

    queue_path = pub / "approval-queue.md"
    if not queue_path.exists():
        return  # template not present, skip silently

    content = queue_path.read_text(encoding="utf-8")

    # Build the new row
    date_str = generated_at[:10]
    size = f"{ceo.get('position_size_pct', 0)}% NAV"
    thesis_short = (ceo.get("thesis") or "")[:80].replace("|", "/")
    invalidation_short = (ceo.get("stop_loss") or "")
    log_link = f"decisions/{ticker}-{generated_at.replace(':', '-')}.json"

    new_row = (
        f"| {date_str} | {ticker} | {action} | {size} "
        f"| {thesis_short} | Stop: {invalidation_short} | [{ticker} memo]({log_link}) |"
    )

    # Insert before the blank line after the table header
    marker = "| Date | Ticker | Action | Size | Thesis (1 line) | Invalidation | Decision Log |"
    header_line = "|------|--------|--------|------|-----------------|-------------|--------------|"
    if marker in content and header_line in content:
        insert_after = content.index(header_line) + len(header_line)
        content = content[:insert_after] + "\n" + new_row + content[insert_after:]
        queue_path.write_text(content, encoding="utf-8")
```

- [ ] **Step 2: Call `_update_approval_queue` after writing artifacts**

In the `main()` function of `cli.py`, after `_append_jsonl(log_path, ...)`, add:

```python
    _update_approval_queue(pub, ticker, ceo, ctx["generated_at"])
```

- [ ] **Step 3: Test manually (dry run)**

```bash
cd step3-debate-decision
python -c "
from axe_decision.cli import _update_approval_queue
from pathlib import Path
pub = Path('../step6-dashboard/public')
fake_ceo = {'action': 'BUY', 'position_size_pct': 5, 'thesis': 'Test thesis for AAPL', 'stop_loss': '185.00'}
_update_approval_queue(pub, 'AAPL', fake_ceo, '2026-04-16T10:00:00Z')
print('done')
"
```

Check that a new row appeared in `step6-dashboard/public/approval-queue.md`:
```bash
head -30 step6-dashboard/public/approval-queue.md
```
Expected: new AAPL row under `## Pending approvals`

- [ ] **Step 4: Commit**

```bash
git add step3-debate-decision/axe_decision/cli.py step6-dashboard/public/approval-queue.md
git commit -m "feat(decision): auto-append BUY/SELL/HOLD decisions to approval-queue.md"
```

---

## Task 6: Auto-chain decision after specialists

**Files:**
- Modify: `step7-automation/axe_orchestrator/runners.py`

Currently `run_specialists()` runs fundamental/technical/macro per symbol but stops there. Add `run_specialists_with_decision()` that chains into `run_decision()` per symbol.

- [ ] **Step 1: Add `run_specialists_with_decision` to runners.py**

In `step7-automation/axe_orchestrator/runners.py`, replace `run_specialists` with:

```python
def run_specialists(ticker: str | None = None) -> int:
    """Run fundamental/technical/macro for a single ticker or all portfolio symbols."""
    portfolio_rc = run_portfolio()
    if portfolio_rc != 0:
        return portfolio_rc
    failures = 0
    symbols = [ticker.upper()] if ticker else portfolio_symbols()
    if not symbols:
        return 1
    for symbol in symbols:
        failures += run_fundamental(symbol)
        failures += run_technical(symbol)
        failures += run_macro(symbol)
    return 0 if failures == 0 else failures


def run_specialists_and_decide(ticker: str | None = None) -> int:
    """Run specialists then immediately run the decision memo for each symbol."""
    rc = run_specialists(ticker)
    if rc != 0:
        return rc
    symbols = [ticker.upper()] if ticker else portfolio_symbols()
    failures = 0
    for symbol in symbols:
        failures += run_decision(symbol)
    return 0 if failures == 0 else failures
```

- [ ] **Step 2: Wire `specialists_decide` as a CLI/API target**

In `runners.py`, update `AGENT_ORDER` to include `specialists_decide`:
```python
AGENT_ORDER = (
    "portfolio",
    "alpha",
    "news",
    "specialists",
    "specialists_decide",
    "opportunities",
    "fundamental",
    "technical",
    "macro",
    "decision",
)
```

In `step7-automation/axe_orchestrator/api.py`, add to `AGENT_RUNNERS`:
```python
"specialists_decide": runners.run_specialists_and_decide,
```

In `step7-automation/axe_orchestrator/cli.py`, add `specialists_decide` to the ARG_TARGETS if needed. Find the section `ARG_TARGETS = {"fundamental", "technical", "macro", "decision", "opportunities"}` and check — `specialists_decide` takes no required ticker so it does NOT need to be in ARG_TARGETS.

- [ ] **Step 3: Add the button to RefreshBar**

In `step6-dashboard/src/components/RefreshBar.jsx`, add to the `TARGETS` array:
```jsx
  { id: 'specialists_decide', label: 'Specialists + Decision' },
```

- [ ] **Step 4: Test the new target CLI**

```bash
cd step7-automation
python -m axe_orchestrator.cli run specialists_decide --help 2>&1 | head -5
```
Expected: no "unknown target" error (it accepts it)

- [ ] **Step 5: Verify build**

```bash
cd step6-dashboard && npm run build 2>&1 | tail -5
```

- [ ] **Step 6: Commit**

```bash
git add step7-automation/axe_orchestrator/runners.py step7-automation/axe_orchestrator/api.py step6-dashboard/src/components/RefreshBar.jsx
git commit -m "feat(orchestrator): add specialists_decide target — runs specialists then decision per symbol"
```

---

## Task 7: Boot scripts

**Files:**
- Create: `scripts/dev.sh`
- Create: `scripts/refresh.sh`

- [ ] **Step 1: Create scripts directory and dev.sh**

```bash
mkdir -p scripts
```

Create `scripts/dev.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."

echo ""
echo "  AXE CAPITAL — dev launcher"
echo "  ─────────────────────────────────────────"
echo ""

# Check .env
if [ ! -f "$ROOT/.env" ]; then
  echo "  ERROR: .env not found at $ROOT/.env"
  echo "  Copy .env.example and fill in your keys."
  exit 1
fi

# Start API (step7)
echo "  Starting API (step7) on :8000 ..."
cd "$ROOT/step7-automation"
uvicorn axe_orchestrator.api:app --port 8000 --log-level warning &
API_PID=$!

# Give API a moment to start
sleep 2

# Health check
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
  echo "  API ready → http://localhost:8000"
else
  echo "  WARNING: API did not respond — dashboard will run in file-only mode"
fi

# Start dashboard (step6)
echo "  Starting dashboard (step6) on :5173 ..."
cd "$ROOT/step6-dashboard"
npm run dev &
DASH_PID=$!

echo ""
echo "  Dashboard → http://localhost:5173"
echo "  API      → http://localhost:8000"
echo ""
echo "  Press Ctrl+C to stop both."
echo ""

# On Ctrl+C, kill both
trap "kill $API_PID $DASH_PID 2>/dev/null; echo ''; echo '  Stopped.'; exit 0" INT TERM

wait
```

- [ ] **Step 2: Create scripts/refresh.sh**

Create `scripts/refresh.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."

TARGET="${1:-}"

if [ -z "$TARGET" ]; then
  echo "Usage: ./scripts/refresh.sh <target>"
  echo ""
  echo "Targets:"
  echo "  portfolio          — refresh portfolio from IBKR"
  echo "  alpha              — run alpha hunter"
  echo "  news               — run news ingestion"
  echo "  specialists        — run fundamental/technical/macro for all holdings"
  echo "  specialists_decide — run specialists + decision memo"
  echo "  opportunities      — run for top alpha opportunities"
  echo "  all                — portfolio + alpha + news"
  exit 1
fi

echo "[axe refresh] target: $TARGET"
cd "$ROOT/step7-automation"
python -m axe_orchestrator.cli run "$TARGET"
echo "[axe refresh] done."
```

- [ ] **Step 3: Make scripts executable**

```bash
chmod +x scripts/dev.sh scripts/refresh.sh
```

- [ ] **Step 4: Test refresh.sh (no-arg gives usage)**

```bash
./scripts/refresh.sh 2>&1
```
Expected: prints usage with target list, exits cleanly

- [ ] **Step 5: Commit**

```bash
git add scripts/dev.sh scripts/refresh.sh
git commit -m "feat(ops): add scripts/dev.sh and scripts/refresh.sh for one-command startup and refresh"
```

---

## Task 8: Archive pruning (keep last 90 days of decisions)

**Files:**
- Modify: `step3-debate-decision/axe_decision/cli.py`

- [ ] **Step 1: Add `_prune_decision_archive` to cli.py**

Add after `_update_approval_queue`:

```python
def _prune_decision_archive(archive_dir: Path, keep_days: int = 90) -> None:
    """Remove decision JSON files older than keep_days. Keeps decision-latest.json untouched."""
    import time
    cutoff = time.time() - (keep_days * 86400)
    for f in archive_dir.glob("*.json"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
```

- [ ] **Step 2: Call pruning after writing archive**

In `main()`, after `_atomic_write_json(archive_path, artifact)`:

```python
    _prune_decision_archive(archive_dir)
```

- [ ] **Step 3: Verify no test-breaking side effects**

```bash
cd step3-debate-decision
python -c "
from axe_decision.cli import _prune_decision_archive
from pathlib import Path
import tempfile, time, os

with tempfile.TemporaryDirectory() as d:
    p = Path(d)
    # Create a 'old' file
    old = p / 'OLD-2020-01-01.json'
    old.write_text('{}')
    os.utime(old, (0, 0))  # set mtime to epoch
    # Create a 'new' file
    new = p / 'NEW-2026-04-16.json'
    new.write_text('{}')
    _prune_decision_archive(p, keep_days=90)
    assert not old.exists(), 'old file should be pruned'
    assert new.exists(), 'new file should be kept'
    print('pruning test passed')
"
```

- [ ] **Step 4: Commit**

```bash
git add step3-debate-decision/axe_decision/cli.py
git commit -m "feat(decision): prune decision archive files older than 90 days"
```

---

## Final: Verify complete App.jsx structure

- [ ] **Step 1: Confirm App.jsx panel order**

`step6-dashboard/src/App.jsx` should now import and render panels in this order:
1. `RefreshBar`
2. `PortfolioPanel`
3. `TargetsPanel`
4. `AlphaPanel` + `NewsPanel` (side by side)
5. `AgentStatusPanel` + `TraceViewerPanel` (side by side)
6. `DecisionReportPanel`
7. `AnalystReportsPanel`
8. `WeeklyReviewPanel`
9. `DecisionArchivePanel`

No imports of `DecisionLogPanel` or `RunbookPanel`.

- [ ] **Step 2: Full build check**

```bash
cd step6-dashboard && npm run build 2>&1 | tail -10
```
Expected: clean build, 0 errors

- [ ] **Step 3: Update To-Do.md — check off completed tasks**

In `/home/tiger/.openclaw/workspace/obsidian-vault/To-Do.md`, mark these done:
- Phase 1: Decision Report panel ✅
- Phase 1: Analyst Reports panel ✅
- Phase 1: Wire CEO → Approval Queue ✅
- Phase 1: Remove orphaned components ✅
- Phase 2: `./scripts/dev.sh` ✅
- Phase 2: `./scripts/refresh.sh` ✅
- Phase 3: Auto-chain specialists → decision ✅
- Phase 3: Weekly Review panel ✅
- Phase 3: Archive pruning ✅
