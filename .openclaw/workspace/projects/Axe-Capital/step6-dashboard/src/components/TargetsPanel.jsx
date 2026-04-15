import { useEffect, useMemo, useState } from 'react'
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

function Badge({ label, className = '' }) {
  return (
    <span className={`ui-badge text-axe-dim border-axe-border bg-axe-muted/20 ${className}`}>{label}</span>
  )
}

function resolveTargetPrice({ last, avg, profit_target_price, profit_target_pct }) {
  const base = avg ?? last
  if (profit_target_price != null) return profit_target_price
  if (profit_target_pct != null && base != null) return base * (1 + profit_target_pct / 100)
  return null
}

function resolveStopPrice({ last, avg, stop_price, stop_pct }) {
  const base = avg ?? last
  if (stop_price != null) return stop_price
  if (stop_pct != null && base != null) return base * (1 + stop_pct / 100)
  return null
}

function proximityPct({ last, level }) {
  if (last == null || level == null) return null
  return ((last - level) / level) * 100
}

function StatusPill({ status }) {
  const cls =
    status === 'BREACHED'
      ? 'bg-red-900/20 text-axe-red border-red-800/60'
      : status === 'NEAR'
        ? 'bg-amber-900/15 text-amber-300 border-amber-800/60'
        : status === 'OK'
          ? 'bg-emerald-900/10 text-emerald-300 border-emerald-800/60'
          : 'bg-axe-muted/10 text-axe-dim border-axe-border'
  return <span className={`text-[11px] px-2 py-0.5 rounded-full border ${cls}`}>{status}</span>
}

export default function TargetsPanel() {
  const [portfolio, setPortfolio] = useState(null)
  const [targets, setTargets] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    Promise.all([
      fetchJsonWithFallback({ filePath: '/portfolio.json' }),
      fetchJsonWithFallback({ filePath: '/targets.json' }),
    ])
      .then(([p, t]) => {
        if (cancelled) return
        setPortfolio(p)
        setTargets(t)
        setLoading(false)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const rows = useMemo(() => {
    if (!portfolio) return []
    const byId = new Map()
    const tpos = targets?.positions ?? []
    for (const tp of tpos) {
      const key = tp.id ?? tp.symbol
      if (key) byId.set(key, tp)
    }

    return (portfolio.positions ?? []).map((p) => {
      const key = p.symbol
      const tp = byId.get(key) ?? null

      const last = p.last_price ?? p.last
      const avg = p.avg_price

      const targetPrice = resolveTargetPrice({
        last,
        avg,
        profit_target_price: tp?.profit_target_price ?? null,
        profit_target_pct: tp?.profit_target_pct ?? null,
      })

      const stopPrice = resolveStopPrice({
        last,
        avg,
        stop_price: tp?.stop_price ?? null,
        stop_pct: tp?.stop_pct ?? null,
      })

      const distToTargetVsLastPct =
        targetPrice == null || last == null || last === 0 ? null : ((targetPrice - last) / last) * 100
      const distToTargetVsAvgPct =
        targetPrice == null || avg == null || avg === 0 ? null : ((targetPrice - avg) / avg) * 100
      const distToStopPct = stopPrice == null ? null : ((last - stopPrice) / last) * 100

      const stopProx = proximityPct({ last, level: stopPrice })

      let status = 'NO_RULES'
      if (stopPrice != null) {
        if (last < stopPrice) status = 'BREACHED'
        else if (stopProx != null && stopProx <= 3) status = 'NEAR'
        else status = 'OK'
      }

      const needsConfig = targetPrice == null || stopPrice == null

      return {
        symbol: p.symbol,
        sector: p.sector_tag,
        shares: p.shares,
        weight_pct: p.weight_pct,
        last,
        avg,
        targetPrice,
        stopPrice,
        distToTargetVsAvgPct,
        distToTargetVsLastPct,
        distToStopPct,
        status,
        needsConfig,
        comment: tp?.comment ?? '',
      }
    })
  }, [portfolio, targets])

  const sorted = useMemo(() => {
    const rank = (s) => (s === 'BREACHED' ? 0 : s === 'NEAR' ? 1 : s === 'OK' ? 2 : 3)
    return [...rows].sort((a, b) => {
      const ra = rank(a.status)
      const rb = rank(b.status)
      if (ra !== rb) return ra - rb
      const ca = a.needsConfig ? 0 : 1
      const cb = b.needsConfig ? 0 : 1
      if (ca !== cb) return ca - cb
      return (b.weight_pct ?? 0) - (a.weight_pct ?? 0)
    })
  }, [rows])

  if (loading) {
    return <section className="panel-card"><div className="text-sm text-axe-dim">Loading targets…</div></section>
  }

  if (error) {
    return <section className="panel-card"><div className="text-sm text-red-300">Failed to load targets: {error}</div></section>
  }

  const configured = sorted.filter((r) => !r.needsConfig).length
  const breached = sorted.filter((r) => r.status === 'BREACHED').length
  const near = sorted.filter((r) => r.status === 'NEAR').length

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="panel-title">Panel 2 — Watchlist & Targets</div>
          <p className="text-axe-dim text-xs mt-1">
            Profit target + stop rules from targets.json. Percent bases: avg cost (fallback to last).
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <Badge label={`${configured}/${sorted.length} configured`} />
          <Badge
            label={`${breached} breached`}
            className={breached > 0 ? 'text-red-300 border-red-700/60 bg-red-900/10' : ''}
          />
          <Badge
            label={`${near} near stop`}
            className={near > 0 ? 'text-amber-300 border-amber-700/60 bg-amber-900/10' : ''}
          />
        </div>
      </div>

      <div className="bg-axe-bg/30 border border-axe-border rounded-lg overflow-hidden mt-4">
        <div className="px-4 py-3 border-b border-axe-border flex items-center justify-between">
          <span className="text-axe-text text-sm font-medium">Targets Table</span>
          <span className="text-axe-dim text-xs">Configure in public/targets.json</span>
        </div>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th className="pl-4">Symbol</th>
                <th>Last</th>
                <th>Avg</th>
                <th>Target $</th>
                <th>Δ vs avg cost</th>
                <th>Δ vs last</th>
                <th>Stop $</th>
                <th>Dist→Stop%</th>
                <th>Status</th>
                <th>Config</th>
                <th className="pr-4">Notes</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((r) => (
                <tr key={r.symbol}>
                  <td className="pl-4 font-semibold text-axe-text">{r.symbol}</td>
                  <td className="text-axe-text">${fmt(r.last)}</td>
                  <td className="text-axe-dim">${fmt(r.avg)}</td>
                  <td className={r.targetPrice == null ? 'text-axe-red' : 'text-axe-text'}>
                    {r.targetPrice == null ? '—' : `$${fmt(r.targetPrice)}`}
                  </td>
                  <td className={pnlClass(r.distToTargetVsAvgPct)}>
                    {r.distToTargetVsAvgPct == null ? '—' : `${sign(r.distToTargetVsAvgPct)}${fmt(r.distToTargetVsAvgPct)}%`}
                  </td>
                  <td className={pnlClass(r.distToTargetVsLastPct)}>
                    {r.distToTargetVsLastPct == null ? '—' : `${sign(r.distToTargetVsLastPct)}${fmt(r.distToTargetVsLastPct)}%`}
                  </td>
                  <td className={r.stopPrice == null ? 'text-axe-red' : 'text-axe-dim'}>
                    {r.stopPrice == null ? '—' : `$${fmt(r.stopPrice)}`}
                  </td>
                  <td className={r.distToStopPct != null && r.distToStopPct < 0 ? 'pnl-neg font-medium' : 'text-axe-dim'}>
                    {r.distToStopPct == null ? '—' : `${sign(r.distToStopPct)}${fmt(r.distToStopPct)}%`}
                  </td>
                  <td>
                    <StatusPill status={r.status} />
                  </td>
                  <td className={r.needsConfig ? 'text-axe-red font-medium' : 'text-emerald-300'}>
                    {r.needsConfig ? 'MISSING' : 'OK'}
                  </td>
                  <td className="pr-4 text-left text-axe-dim max-w-[240px] truncate">{r.comment || '—'}</td>
                </tr>
              ))}

              {sorted.length === 0 && (
                <tr>
                  <td colSpan={11} className="pl-4 pr-4 py-6 text-center text-axe-dim text-xs">
                    No positions found in portfolio.json.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="text-axe-dim text-xs mt-3">
        Edit <span className="text-axe-text">public/targets.json</span> to set targets/stops.
      </div>
    </section>
  )
}
