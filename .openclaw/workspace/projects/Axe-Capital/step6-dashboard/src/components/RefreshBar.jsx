import { useEffect, useState } from 'react'
import { fetchHealthStatus, triggerRefresh } from '../lib/api'

const TARGETS = [
  { id: 'all', label: 'Run all' },
  { id: 'portfolio', label: 'Portfolio' },
  { id: 'alpha', label: 'Alpha' },
  { id: 'news', label: 'News' },
  { id: 'specialists', label: 'Specialists' },
  { id: 'specialists_decide', label: 'Specialists + Decision' },
  { id: 'opportunities', label: 'Opportunities' },
  { id: 'decision', label: 'Decision' },
]

function formatTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function FreshnessChip({ label, status }) {
  const tone =
    status === 'fresh'
      ? 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
      : status === 'stale'
        ? 'text-amber-300 border-amber-700/60 bg-amber-900/10'
        : 'text-red-300 border-red-700/60 bg-red-900/10'

  return <span className={`ui-badge ${tone}`}>{label}</span>
}

export default function RefreshBar({ onRefreshComplete }) {
  const [health, setHealth] = useState(null)
  const [mode, setMode] = useState('checking')
  const [runningTarget, setRunningTarget] = useState(null)
  const [error, setError] = useState(null)
  const [lastResult, setLastResult] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchHealthStatus()
      .then(({ data, source }) => {
        if (cancelled) return
        setHealth(data)
        setMode(source === 'api' ? 'Hybrid' : 'File-only')
      })
      .catch(() => {
        if (cancelled) return
        setHealth(null)
        setMode('Unavailable')
      })
    return () => {
      cancelled = true
    }
  }, [])

  async function handleRefresh(target) {
    setRunningTarget(target)
    setError(null)
    try {
      const result = await triggerRefresh(target)
      setLastResult(result)
      const { data, source } = await fetchHealthStatus().catch(() => ({ data: null, source: 'file' }))
      setHealth(data)
      setMode(source === 'api' ? 'Hybrid' : 'File-only')
      onRefreshComplete?.(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setRunningTarget(null)
    }
  }

  const artifacts = health?.artifacts || {}

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="panel-title">System State</div>
          <p className="text-axe-dim text-xs mt-1">
            API-backed refresh when available, static-file fallback for reading.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <FreshnessChip label={`portfolio: ${artifacts.portfolio?.status || 'unknown'}`} status={artifacts.portfolio?.status} />
          <FreshnessChip label={`alpha: ${artifacts.alpha?.status || 'unknown'}`} status={artifacts.alpha?.status} />
          <FreshnessChip label={`news: ${artifacts.news?.status || 'unknown'}`} status={artifacts.news?.status} />
          <FreshnessChip label={`analysts: ${artifacts.analyst_reports?.status || 'unknown'}`} status={artifacts.analyst_reports?.status} />
          <FreshnessChip label={`decision: ${artifacts.decision?.status || 'unknown'}`} status={artifacts.decision?.status} />
          <FreshnessChip label={`traces: ${artifacts.traces?.status || 'unknown'}`} status={artifacts.traces?.status} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-4 mt-4">
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {TARGETS.map((target) => {
              const busy = runningTarget === target.id
              return (
                <button
                  key={target.id}
                  className={target.id === 'all' ? 'ui-button' : 'ui-button-secondary'}
                  onClick={() => handleRefresh(target.id)}
                  disabled={runningTarget !== null}
                >
                  {busy ? `Running ${target.label}...` : target.label}
                </button>
              )
            })}
          </div>
          {error && <div className="text-sm text-red-300">Refresh failed: {error}</div>}
          {!error && lastResult && (
            <div className="text-sm text-axe-dim">
              Last action: <span className="text-axe-text">{lastResult.target}</span>
              {' · '}
              {lastResult.ok ? 'completed' : `completed with ${lastResult.failure_count} failure(s)`}
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="stat-card">
            <div className="text-axe-dim text-xs uppercase tracking-wider">Mode</div>
            <div className="text-lg font-semibold text-axe-text mt-1">{mode}</div>
            <div className="text-axe-dim text-xs mt-1">Refresh controls require the Step 7 API.</div>
          </div>
          <div className="stat-card">
            <div className="text-axe-dim text-xs uppercase tracking-wider">Health snapshot</div>
            <div className="text-lg font-semibold text-axe-text mt-1">{formatTime(health?.generated_at)}</div>
            <div className="text-axe-dim text-xs mt-1">Latest dashboard-wide freshness check.</div>
          </div>
        </div>
      </div>
    </section>
  )
}
