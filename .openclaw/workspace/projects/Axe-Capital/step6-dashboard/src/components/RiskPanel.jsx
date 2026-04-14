import { useEffect, useMemo, useState } from 'react'

const fmt = (n, digits = 2) =>
  n == null ? '—' : n.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits })

function StatCard({ label, value, sub, valueClass = '' }) {
  return (
    <div className="stat-card flex flex-col gap-1">
      <span className="text-axe-dim text-xs uppercase tracking-wider">{label}</span>
      <span className={`text-xl font-semibold tabular-nums ${valueClass}`}>{value}</span>
      {sub && <span className="text-axe-dim text-xs">{sub}</span>}
    </div>
  )
}

function Badge({ label, className = '' }) {
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-full border border-axe-border bg-axe-muted/20 text-axe-dim ${className}`}>
      {label}
    </span>
  )
}

export default function RiskPanel() {
  const [portfolio, setPortfolio] = useState(null)
  const [targets, setTargets] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/portfolio.json').then((r) => (r.ok ? r.json() : Promise.reject(new Error(`portfolio HTTP ${r.status}`)))),
      fetch('/targets.json').then((r) => (r.ok ? r.json() : Promise.reject(new Error(`targets HTTP ${r.status}`))))
    ])
      .then(([p, t]) => {
        setPortfolio(p)
        setTargets(t)
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [])

  const model = useMemo(() => {
    if (!portfolio) return null
    const positions = portfolio.positions ?? []

    const tpos = targets?.positions ?? []
    const byId = new Map()
    for (const tp of tpos) {
      const key = tp.id ?? tp.symbol
      if (key) byId.set(key, tp)
    }

    let nav = portfolio.summary?.nav ?? null
    if (nav == null) {
      const positionsValue = portfolio.summary?.positions_value ?? 0
      const cash = portfolio.summary?.cash ?? 0
      nav = positionsValue + cash
    }

    let totalRiskUsd = 0
    let configuredCount = 0

    const rows = positions.map((p) => {
      const tp = byId.get(p.symbol) ?? null
      const last = p.last_price ?? p.last
      const stop = tp?.stop_price ?? p.stop_loss_level ?? null
      const shares = p.shares ?? null
      let riskUsd = null
      if (last != null && stop != null && shares != null) {
        riskUsd = Math.max(last - stop, 0) * shares
        totalRiskUsd += riskUsd
        configuredCount += 1
      }
      const wt = p.weight_pct ?? null
      return { symbol: p.symbol, weight_pct: wt, last, stop, shares, riskUsd }
    })

    const riskPctNav = nav ? (totalRiskUsd / nav) * 100 : null

    const top = [...rows]
      .filter((r) => r.riskUsd != null)
      .sort((a, b) => b.riskUsd - a.riskUsd)
      .slice(0, 8)

    return { nav, positionsCount: positions.length, configuredCount, totalRiskUsd, riskPctNav, top }
  }, [portfolio, targets])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-axe-dim text-sm">
        Loading risk model...
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
            Panel 3 — Risk Snapshot
          </h2>
          <p className="text-axe-dim text-xs mt-0.5">
            Approx. stop-loss risk per position (USD) and total book risk (static, derived from portfolio + targets)
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <Badge label={`${model?.configuredCount ?? 0}/${model?.positionsCount ?? 0} w/ stop`} />
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard
          label="Total Risk $"
          value={model?.totalRiskUsd != null ? `$${Math.round(model.totalRiskUsd).toLocaleString()}` : '—'}
          sub="Sum(max(last-stop,0)*shares)"
          valueClass={model?.totalRiskUsd > 0 ? 'text-amber-300' : ''}
        />
        <StatCard
          label="Risk % NAV"
          value={model?.riskPctNav != null ? `${fmt(model.riskPctNav, 2)}%` : '—'}
          sub="Total risk / NAV"
          valueClass={model?.riskPctNav != null && model.riskPctNav > 5 ? 'text-axe-red' : model?.riskPctNav > 2 ? 'text-amber-300' : 'text-emerald-300'}
        />
        <StatCard
          label="NAV"
          value={model?.nav != null ? `$${Math.round(model.nav).toLocaleString()}` : '—'}
          sub="IBKR total"
        />
      </div>

      <div className="bg-axe-surface border border-axe-border rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-axe-border flex items-center justify-between">
          <span className="text-axe-text text-sm font-medium">Top Risk Positions</span>
          <span className="text-axe-dim text-xs">largest $ risk to stop (approx.)</span>
        </div>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th className="pl-4">Symbol</th>
                <th>Last</th>
                <th>Stop</th>
                <th>Shares</th>
                <th>Wt%</th>
                <th className="pr-4">Risk $</th>
              </tr>
            </thead>
            <tbody>
              {(model?.top ?? []).map((r) => (
                <tr key={r.symbol}>
                  <td className="pl-4 font-semibold text-axe-text">{r.symbol}</td>
                  <td className="text-axe-text">${fmt(r.last)}</td>
                  <td className="text-axe-dim">{r.stop == null ? '—' : `$${fmt(r.stop)}`}</td>
                  <td className="text-axe-dim">{r.shares == null ? '—' : fmt(r.shares, r.shares % 1 === 0 ? 0 : 4)}</td>
                  <td className="text-axe-dim">{r.weight_pct == null ? '—' : `${fmt(r.weight_pct, 1)}%`}</td>
                  <td className="pr-4 text-axe-text font-medium">{r.riskUsd == null ? '—' : `$${Math.round(r.riskUsd).toLocaleString()}`}</td>
                </tr>
              ))}
              {(model?.top ?? []).length === 0 && (
                <tr>
                  <td colSpan={6} className="pl-4 pr-4 py-6 text-center text-axe-dim text-xs">
                    No stops detected. Add stop_price in targets.json (or ensure portfolio.json contains stop_loss_level).
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="text-axe-dim text-xs">
        Note: This is an approximation. It assumes immediate fill at stop and uses stop_price from targets.json when present, otherwise portfolio.json stop_loss_level.
      </div>
    </div>
  )
}

