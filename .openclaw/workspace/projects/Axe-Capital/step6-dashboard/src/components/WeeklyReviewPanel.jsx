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
