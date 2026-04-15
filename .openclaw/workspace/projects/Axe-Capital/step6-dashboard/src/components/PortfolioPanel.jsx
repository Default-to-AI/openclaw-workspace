import { useEffect, useMemo, useState } from 'react'
import { fetchHealth, fetchJsonWithFallback } from '../lib/api'

const fmt = (n, digits = 2) =>
  n == null ? '—' : n.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits })

const fmtUSD = (n) =>
  n == null ? '—' : '$' + Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })

const pnlClass = (n) => {
  if (n == null) return 'text-axe-dim'
  if (n > 0) return 'pnl-pos'
  if (n < 0) return 'pnl-neg'
  return 'pnl-flat'
}

const sign = (n) => (n > 0 ? '+' : '')

function AlertBadge({ status }) {
  return <span className={`alert-pill alert-${status}`}>{status}</span>
}

function FreshnessBadge({ health }) {
  const portfolio = health?.artifacts?.portfolio
  if (!portfolio) return null
  const tone =
    portfolio.status === 'fresh'
      ? 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
      : portfolio.status === 'stale'
        ? 'text-amber-300 border-amber-700/60 bg-amber-900/10'
        : 'text-red-300 border-red-700/60 bg-red-900/10'

  const label =
    portfolio.age_min != null ? `${portfolio.status} · ${portfolio.age_min}m` : portfolio.status

  return <span className={`ui-badge ${tone}`}>{label}</span>
}

function StatCard({ label, value, sub, valueClass = '' }) {
  return (
    <div className="stat-card flex flex-col gap-1">
      <span className="text-axe-dim text-xs uppercase tracking-wider">{label}</span>
      <span className={`text-xl font-semibold tabular-nums ${valueClass}`}>{value}</span>
      {sub && <span className="text-axe-dim text-xs">{sub}</span>}
    </div>
  )
}

function SectorBar({ sector, pct, maxPct }) {
  const barWidth = Math.min((pct / maxPct) * 100, 100)
  const color = pct > 50 ? 'bg-amber-500' : pct > 25 ? 'bg-axe-blue' : 'bg-axe-accent'

  return (
    <div className="flex items-center gap-3">
      <span className="text-axe-dim text-xs w-40 truncate shrink-0">{sector}</span>
      <div className="flex-1 h-1.5 bg-axe-muted/30 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${barWidth}%` }} />
      </div>
      <span className="text-axe-text text-xs tabular-nums w-12 text-right">{fmt(pct, 1)}%</span>
    </div>
  )
}

export default function PortfolioPanel() {
  const [data, setData] = useState(null)
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchJsonWithFallback({ filePath: '/portfolio.json' })
      .then((payload) => {
        if (cancelled) return
        setData(payload)
        setLoading(false)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
        setLoading(false)
      })

    fetchHealth()
      .then((payload) => {
        if (cancelled) return
        setHealth(payload)
      })
      .catch(() => {
        if (cancelled) return
        setHealth(null)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const maxSectorPct = useMemo(() => {
    if (!data?.sector_weights?.length) return 1
    return Math.max(...data.sector_weights.map((s) => s.ibkr_pct), 1)
  }, [data])

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="panel-title">Panel 1 — Portfolio State</div>
            <FreshnessBadge health={health} />
          </div>
          <p className="text-axe-dim text-xs mt-1">
            IBKR snapshot · as of {data?.review_date || '—'}
          </p>
        </div>

        {data?.summary && (
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="flex items-center gap-1.5 text-axe-red">
              <span className="w-2 h-2 rounded-sm bg-red-600" />
              {data.summary.red_count} RED
            </span>
            <span className="flex items-center gap-1.5 text-amber-400">
              <span className="w-2 h-2 rounded-sm bg-amber-500" />
              {data.summary.yellow_count} YELLOW
            </span>
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-sm bg-emerald-500" />
              {data.summary.green_count} GREEN
            </span>
          </div>
        )}
      </div>

      {loading && <div className="mt-4 text-sm text-axe-dim">Loading portfolio…</div>}
      {error && <div className="mt-4 text-sm text-red-300">Failed to load portfolio: {error}</div>}

      {!loading && !error && data && (
        <div className="space-y-5 mt-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <StatCard label="NAV" value={`$${Math.round(data.summary.nav).toLocaleString()}`} sub="IBKR total" />
            <StatCard
              label="Positions"
              value={`$${Math.round(data.summary.positions_value).toLocaleString()}`}
              sub={`${data.positions.length} holdings`}
            />
            <StatCard
              label="Cash"
              value={`$${Math.round(data.summary.cash).toLocaleString()}`}
              sub={`${data.summary.cash_pct}% of NAV`}
              valueClass={data.summary.cash_pct < 5 ? 'pnl-neg' : 'pnl-pos'}
            />
            <StatCard
              label="Unrealized P&L"
              value={`${sign(data.summary.total_unrealized_pl)}$${Math.abs(Math.round(data.summary.total_unrealized_pl)).toLocaleString()}`}
              sub={`${sign(data.summary.total_unrealized_pl_pct)}${fmt(data.summary.total_unrealized_pl_pct)}%`}
              valueClass={pnlClass(data.summary.total_unrealized_pl)}
            />
            <StatCard
              label="Alerts"
              value={`${data.summary.red_count} / ${data.summary.yellow_count}`}
              sub="RED / YELLOW"
              valueClass={data.summary.red_count > 0 ? 'pnl-neg' : 'pnl-pos'}
            />
            <div className={`stat-card flex flex-col gap-1 ${data.hishtalmut?.priority ? 'border-amber-700/60 bg-amber-900/10' : ''}`}>
              <span className="text-axe-dim text-xs uppercase tracking-wider">Hishtalmut</span>
              <span className={`text-xl font-semibold tabular-nums ${data.hishtalmut?.priority ? 'text-amber-400' : 'text-axe-text'}`}>
                ₪{(data.hishtalmut?.remaining_2026_ils ?? 0).toLocaleString()}
              </span>
              <span className="text-axe-dim text-xs">
                {data.hishtalmut?.priority ? 'PRIORITY · room remaining' : 'maxed for 2026'}
              </span>
            </div>
          </div>

          <div className="bg-axe-bg/30 border border-axe-border rounded-lg overflow-hidden">
            <div className="px-4 py-3 border-b border-axe-border flex items-center justify-between">
              <span className="text-axe-text text-sm font-medium">Positions</span>
              <span className="text-axe-dim text-xs">{data.positions.length} holdings · sorted by alert severity</span>
            </div>
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th className="pl-4">Symbol</th>
                    <th>Sector</th>
                    <th>Shares</th>
                    <th>Last</th>
                    <th>Chg%</th>
                    <th>Avg Cost</th>
                    <th>Cost Basis</th>
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
                  {data.positions.map((p) => (
                    <tr key={p.symbol}>
                      <td className="pl-4 font-semibold text-axe-text">{p.symbol}</td>
                      <td className="text-left text-axe-dim max-w-[120px] truncate">{p.sector_tag}</td>
                      <td>{fmt(p.shares, p.shares % 1 === 0 ? 0 : 4)}</td>
                      <td className="text-axe-text">${fmt(p.last_price)}</td>
                      <td className={pnlClass(p.change_pct)}>
                        {p.change_pct != null ? `${sign(p.change_pct)}${fmt(p.change_pct)}%` : '—'}
                      </td>
                      <td>${fmt(p.avg_price)}</td>
                      <td>${fmt(p.cost_basis, 0)}</td>
                      <td className="text-axe-text font-medium">${fmt(p.market_value, 0)}</td>
                      <td className={pnlClass(p.unrealized_pl)}>
                        {p.unrealized_pl != null ? `${sign(p.unrealized_pl)}${fmtUSD(p.unrealized_pl).replace('-', '')}` : '—'}
                      </td>
                      <td className={`font-medium ${pnlClass(p.unrealized_pl_pct)}`}>
                        {p.unrealized_pl_pct != null ? `${sign(p.unrealized_pl_pct)}${fmt(p.unrealized_pl_pct)}%` : '—'}
                      </td>
                      <td className="text-axe-dim">${fmt(p.stop_loss_level)}</td>
                      <td className={p.distance_to_stop_pct != null && p.distance_to_stop_pct < 0 ? 'pnl-neg font-medium' : 'text-axe-dim'}>
                        {p.distance_to_stop_pct != null ? `${sign(p.distance_to_stop_pct)}${fmt(p.distance_to_stop_pct)}%` : '—'}
                      </td>
                      <td className="text-axe-dim">{fmt(p.weight_pct, 1)}%</td>
                      <td className="pr-4">
                        <AlertBadge status={p.alert_status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-axe-bg/30 border border-axe-border rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <span className="text-axe-text text-sm font-medium">Sector Weights (IBKR)</span>
                <span className="text-axe-dim text-xs">% of IBKR book</span>
              </div>
              <div className="space-y-3">
                {data.sector_weights
                  .filter((s) => s.ibkr_pct > 0)
                  .sort((a, b) => b.ibkr_pct - a.ibkr_pct)
                  .map((s) => (
                    <SectorBar key={s.sector} sector={s.sector} pct={s.ibkr_pct} maxPct={maxSectorPct} />
                  ))}
              </div>
            </div>

            <div className="bg-axe-bg/30 border border-axe-border rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <span className="text-axe-text text-sm font-medium">Positions Requiring Attention</span>
                <span className="text-axe-dim text-xs">Stop breached or approaching</span>
              </div>
              <div className="space-y-2">
                {data.positions
                  .filter((p) => p.alert_status === 'RED' || p.alert_status === 'YELLOW')
                  .map((p) => (
                    <div key={p.symbol} className="flex items-center justify-between py-2 border-b border-axe-border/40 last:border-b-0">
                      <div className="flex items-center gap-2.5">
                        <AlertBadge status={p.alert_status} />
                        <span className="font-semibold text-axe-text text-sm">{p.symbol}</span>
                        <span className="text-axe-dim text-xs">{p.sector_tag}</span>
                      </div>
                      <div className="flex items-center gap-4 text-xs tabular-nums">
                        <span className={pnlClass(p.unrealized_pl_pct)}>
                          {p.unrealized_pl_pct != null ? `${sign(p.unrealized_pl_pct)}${fmt(p.unrealized_pl_pct)}%` : '—'}
                        </span>
                        <span className="text-axe-dim">
                          stop ${fmt(p.stop_loss_level)} · dist{' '}
                          <span className={p.distance_to_stop_pct < 0 ? 'text-axe-red font-medium' : 'text-axe-dim'}>
                            {p.distance_to_stop_pct != null ? `${sign(p.distance_to_stop_pct)}${fmt(p.distance_to_stop_pct)}%` : '—'}
                          </span>
                        </span>
                      </div>
                    </div>
                  ))}

                {data.positions.filter((p) => p.alert_status !== 'GREEN').length === 0 && (
                  <p className="text-axe-dim text-xs py-4 text-center">All positions within safe range.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
