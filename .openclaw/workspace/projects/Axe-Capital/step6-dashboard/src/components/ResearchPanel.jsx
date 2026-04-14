import { useEffect, useMemo, useState } from 'react'

function Badge({ label, className = '' }) {
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-full border border-axe-border bg-axe-muted/20 text-axe-dim ${className}`}>
      {label}
    </span>
  )
}

function Card({ title, subtitle, children, right }) {
  return (
    <div className="bg-axe-surface border border-axe-border rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-axe-border flex items-start justify-between gap-4">
        <div>
          <div className="text-axe-text text-sm font-medium">{title}</div>
          {subtitle && <div className="text-axe-dim text-xs mt-0.5">{subtitle}</div>}
        </div>
        {right}
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

function kvFrom(obj, keys) {
  for (const k of keys) {
    if (obj && obj[k] != null) return obj[k]
  }
  return null
}

export default function ResearchPanel() {
  const [weekly, setWeekly] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/weekly-review-latest.json')
      .then((r) => {
        if (!r.ok) throw new Error(`weekly-review HTTP ${r.status}`)
        return r.json()
      })
      .then((d) => {
        setWeekly(d)
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [])

  const spy = weekly?.spy_comparison ?? null
  const alpha = spy?.relative_alpha_pct ?? null
  const reviewDate = weekly?.review_date ?? '—'

  const sector = useMemo(() => {
    const rows = (weekly?.sector_concentration ?? []).slice(0)
    rows.sort((a, b) => (b.ibkr_pct ?? 0) - (a.ibkr_pct ?? 0))
    return rows.slice(0, 8)
  }, [weekly])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-axe-dim text-sm">
        Loading research digest...
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-axe-red text-sm">
        Error: {error}
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-axe-text font-semibold text-base tracking-wide">
            Panel 4 — Research Digest
          </h2>
          <p className="text-axe-dim text-xs mt-0.5">
            Weekly review highlights (static JSON)
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <Badge label={`as of ${reviewDate}`} />
          <Badge
            label={alpha == null ? 'alpha —' : `alpha ${alpha > 0 ? '+' : ''}${alpha}%`}
            className={alpha == null ? '' : alpha > 0 ? 'text-emerald-300 border-emerald-800/60 bg-emerald-900/10' : 'text-axe-red border-red-800/60 bg-red-900/20'}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card
          title="SPY comparison"
          subtitle="Portfolio return vs SPY (same window)"
        >
          <div className="grid grid-cols-2 gap-3">
            <div className="stat-card">
              <div className="text-axe-dim text-xs uppercase tracking-wider">Portfolio return</div>
              <div className="text-xl font-semibold tabular-nums text-axe-text mt-1">
                {kvFrom(spy, ['portfolio_return_pct']) == null ? '—' : `${spy.portfolio_return_pct}%`}
              </div>
            </div>
            <div className="stat-card">
              <div className="text-axe-dim text-xs uppercase tracking-wider">SPY return</div>
              <div className="text-xl font-semibold tabular-nums text-axe-text mt-1">
                {kvFrom(spy, ['spy_return_pct_same_window']) == null ? '—' : `${spy.spy_return_pct_same_window}%`}
              </div>
            </div>
            <div className="stat-card col-span-2">
              <div className="text-axe-dim text-xs uppercase tracking-wider">Relative alpha</div>
              <div className={`text-xl font-semibold tabular-nums mt-1 ${alpha == null ? 'text-axe-dim' : alpha > 0 ? 'text-emerald-300' : 'text-axe-red'}`}>
                {alpha == null ? '—' : `${alpha > 0 ? '+' : ''}${alpha}%`}
              </div>
            </div>
          </div>
        </Card>

        <Card
          title="Sector concentration"
          subtitle="Top IBKR sector weights (from weekly review)"
          right={<Badge label={`${sector.length} shown`} />}
        >
          <div className="space-y-2">
            {sector.map((s) => (
              <div key={s.sector} className="flex items-center justify-between gap-4">
                <div className="text-axe-text text-sm truncate">{s.sector}</div>
                <div className="text-axe-dim text-xs tabular-nums shrink-0">
                  {s.ibkr_pct == null ? '—' : `${s.ibkr_pct}%`} IBKR
                  <span className="text-axe-border px-2">|</span>
                  {s.passive_pct == null ? '—' : `${s.passive_pct}%`} passive
                </div>
              </div>
            ))}
            {sector.length === 0 && (
              <div className="text-axe-dim text-xs">No sector_concentration found in weekly-review-latest.json</div>
            )}
          </div>
        </Card>
      </div>

      <div className="text-axe-dim text-xs">
        Source: <span className="text-axe-text">weekly-review-latest.json</span> (copied into dashboard public/ by automation).
      </div>
    </div>
  )
}

