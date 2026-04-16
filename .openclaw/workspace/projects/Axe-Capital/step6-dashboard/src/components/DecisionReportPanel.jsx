import { useEffect, useState } from 'react'
import { fetchJsonWithFallback, describeError, fmtDate } from '../lib/api'

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
        setError(describeError(err))
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
              <span className="ui-badge text-axe-accent border-axe-accent/40 bg-axe-accent/10 font-bold text-sm px-2.5">{data.ticker}</span>
              <span className={`ui-badge ${actionTone(ceo.action)}`}>{ceo.action || '—'}</span>
              <span className={`ui-badge ${convictionTone(ceo.conviction_1_to_10)} border-axe-border`}>
                conviction {ceo.conviction_1_to_10 ?? '—'}/10
              </span>
              <span className="text-axe-dim">{fmtDate(data.generated_at)}</span>
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
