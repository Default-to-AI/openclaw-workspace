import { useEffect, useState } from 'react'
import { fetchJsonWithFallback, describeError } from '../lib/api'

function convictionTone(score) {
  if (score >= 8) return 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
  if (score >= 6) return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  return 'text-axe-dim border-axe-border bg-axe-muted/20'
}

function OpportunityCard({ opp, rank }) {
  const [open, setOpen] = useState(rank === 1)

  return (
    <article className="border border-axe-border rounded-lg bg-axe-bg/30 p-4">
      <button className="w-full text-left" onClick={() => setOpen((value) => !value)}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="ui-badge text-axe-dim border-axe-border">#{rank}</span>
              <span className="text-lg font-semibold text-axe-text">{opp.ticker}</span>
              <span className="ui-badge text-axe-dim border-axe-border bg-axe-muted/20">{opp.opportunity_type}</span>
              <span className={`ui-badge ${convictionTone(opp.conviction_score)}`}>
                conviction {opp.conviction_score}/10
              </span>
            </div>
            <p className="text-sm text-axe-text mt-3 leading-6">{opp.thesis}</p>
          </div>
          <span className="text-axe-dim text-sm shrink-0">{open ? 'Hide' : 'Expand'}</span>
        </div>
      </button>

      {open && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="space-y-3 text-sm">
            <div>
              <div className="text-axe-dim text-xs uppercase tracking-wider">Trigger</div>
              <div className="text-axe-text mt-1">{opp.trigger_source}</div>
              <div className="text-axe-dim mt-1">{opp.trigger_data_point}</div>
            </div>
            <div>
              <div className="text-axe-dim text-xs uppercase tracking-wider">Why this matters</div>
              <div className="text-axe-text mt-1">{opp.why_retail_is_missing_this}</div>
            </div>
          </div>

          <div className="space-y-3 text-sm">
            <div>
              <div className="text-axe-dim text-xs uppercase tracking-wider">Risk flags</div>
              <div className="text-red-200 mt-1">{opp.risk_flags}</div>
            </div>
            <div>
              <div className="text-axe-dim text-xs uppercase tracking-wider">Base score</div>
              <div className="text-axe-text mt-1">{opp.base_score}</div>
            </div>
          </div>

          <details className="md:col-span-2">
            <summary className="cursor-pointer text-sm text-axe-dim">Raw facts</summary>
            <pre className="mt-3 rounded-lg border border-axe-border bg-axe-bg p-3 text-xs text-axe-text overflow-auto">
              {JSON.stringify(opp.raw_facts, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </article>
  )
}

export default function AlphaPanel() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchJsonWithFallback({ filePath: '/alpha-latest.json' })
      .then((payload) => {
        if (cancelled) return
        setData(payload)
      })
      .catch((err) => {
        if (cancelled) return
        setError(describeError(err))
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section className="panel-card h-full">
      <div className="panel-header">
        <div>
          <div className="panel-title">Alpha Opportunities</div>
          <p className="text-axe-dim text-xs mt-1">
            Ranked opportunities surfaced by Alpha Hunter.
          </p>
        </div>
        <div className="text-axe-dim text-xs">
          {data ? `${(data.top_opportunities || []).length} ideas · ${data.generated_at || 'time unknown'}` : 'loading…'}
        </div>
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load alpha report: {error}</div>}

      {!error && !data && <div className="mt-4 text-sm text-axe-dim">Loading alpha report…</div>}

      {!error && data && (
        <div className="space-y-4 mt-4">
          {(data.top_opportunities || []).length === 0 ? (
            <div className="text-sm text-axe-dim">No opportunities in the latest scan.</div>
          ) : (
            (data.top_opportunities || []).map((opp, index) => (
              <OpportunityCard key={`${opp.ticker}-${index}`} opp={opp} rank={index + 1} />
            ))
          )}
        </div>
      )}
    </section>
  )
}
