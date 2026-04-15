import { useEffect, useMemo, useState } from 'react'
import { fetchHealth, fetchJsonWithFallback } from '../lib/api'

const AGENTS = ['axe_portfolio', 'axe_alpha', 'axe_news', 'axe_decision']

function agentKey(agent) {
  return {
    axe_portfolio: 'portfolio',
    axe_alpha: 'alpha',
    axe_news: 'news',
    axe_decision: 'decision',
  }[agent] || agent
}

function statusTone(status) {
  return {
    success: 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10',
    partial: 'text-amber-300 border-amber-700/60 bg-amber-900/10',
    failed: 'text-red-300 border-red-700/60 bg-red-900/10',
    missing: 'text-axe-dim border-axe-border bg-axe-muted/20',
  }[status] || 'text-axe-dim border-axe-border bg-axe-muted/20'
}

function freshnessTone(status) {
  return {
    fresh: 'text-emerald-300',
    stale: 'text-amber-300',
    missing: 'text-red-300',
  }[status] || 'text-axe-dim'
}

function formatDuration(durationMs) {
  if (durationMs == null) return '—'
  return `${Math.round(durationMs / 1000)}s`
}

export default function AgentStatusPanel({ onOpenTrace = () => {} }) {
  const [index, setIndex] = useState({ runs: [] })
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([
      fetchJsonWithFallback({ filePath: '/traces/index.json' }).catch(() => ({ runs: [] })),
      fetchHealth().catch(() => null),
    ])
      .then(([traceIndex, healthReport]) => {
        if (cancelled) return
        setIndex(traceIndex)
        setHealth(healthReport)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const latestByAgent = useMemo(() => {
    const mapping = {}
    for (const run of index.runs || []) {
      if (!mapping[run.agent]) {
        mapping[run.agent] = run
      }
    }
    return mapping
  }, [index])

  return (
    <section className="panel-card h-full">
      <div className="panel-header">
        <div>
          <div className="panel-title">Panel 5 — Agent Status Board</div>
          <p className="text-axe-dim text-xs mt-1">
            Latest run status, freshness, and trace handoff per agent.
          </p>
        </div>
        <div className="text-axe-dim text-xs">
          {(index.runs || []).length} indexed runs
        </div>
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load agent status: {error}</div>}

      {!error && (
        <div className="space-y-3 mt-4">
          {AGENTS.map((agent) => {
            const run = latestByAgent[agent]
            const freshness = health?.artifacts?.[agentKey(agent)]?.status || 'missing'
            return (
              <div key={agent} className="border border-axe-border rounded-lg bg-axe-bg/30 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-axe-text font-semibold">{agent}</span>
                      <span className={`ui-badge ${statusTone(run?.status || 'missing')}`}>{run?.status || 'missing'}</span>
                    </div>
                    <div className="text-xs text-axe-dim mt-2">
                      duration {formatDuration(run?.duration_ms)} · freshness{' '}
                      <span className={freshnessTone(freshness)}>{freshness}</span>
                    </div>
                    <div className="text-sm text-axe-text mt-3">{run?.summary || 'No runs yet.'}</div>
                  </div>

                  <div className="flex flex-col items-end gap-2">
                    {run?.artifact_written && (
                      <span className="ui-badge text-axe-dim border-axe-border bg-axe-muted/20">{run.artifact_written}</span>
                    )}
                    {run?.run_id && (
                      <button className="ui-button-secondary" onClick={() => onOpenTrace(run.run_id)}>
                        Open trace
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
