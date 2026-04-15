import { useEffect, useState } from 'react'
import { fetchJsonWithFallback } from '../lib/api'

function impactTone(score) {
  if (score >= 9) return 'text-red-200 border-red-700/60 bg-red-900/20'
  if (score >= 7) return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  return 'text-axe-text border-axe-border bg-axe-muted/20'
}

function relevanceTone(value) {
  const tones = {
    held: 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10',
    watchlist: 'text-sky-300 border-sky-700/60 bg-sky-900/10',
    sector: 'text-axe-dim border-axe-border bg-axe-muted/20',
    none: 'text-axe-dim border-axe-border bg-axe-muted/20',
  }
  return tones[value] || tones.none
}

function NewsCard({ item }) {
  return (
    <article className="border border-axe-border rounded-lg bg-axe-bg/30 p-4">
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <span className={`ui-badge ${impactTone(item.impact_score)}`}>impact {item.impact_score}</span>
        <span className={`ui-badge ${relevanceTone(item.portfolio_relevance)}`}>{item.portfolio_relevance}</span>
        {(item.tickers_mentioned || []).map((ticker) => (
          <span key={ticker} className="ui-badge text-axe-text border-axe-border bg-axe-muted/20">{ticker}</span>
        ))}
        <span className="ml-auto text-xs text-axe-dim">{item.source} · {item.published_at}</span>
      </div>

      <a href={item.url} target="_blank" rel="noreferrer" className="text-axe-text font-semibold hover:underline">
        {item.title}
      </a>

      <p className="text-sm text-axe-text mt-3 leading-6">{item.impact_rationale}</p>

      {item.decision_hook && (
        <div className="mt-3 rounded-lg border border-sky-800/50 bg-sky-950/20 p-3 text-sm text-sky-200">
          Decision hook: {item.decision_hook}
        </div>
      )}
    </article>
  )
}

export default function NewsPanel() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchJsonWithFallback({ filePath: '/news-latest.json' })
      .then((payload) => {
        if (cancelled) return
        setData(payload)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section className="panel-card h-full">
      <div className="panel-header">
        <div>
          <div className="panel-title">Panel 4 — Hot News</div>
          <p className="text-axe-dim text-xs mt-1">
            High-impact news only. Noise stays out.
          </p>
        </div>
        <div className="text-axe-dim text-xs">
          {data ? `${data.items_kept} kept of ${data.items_in} · ${data.generated_at || 'time unknown'}` : 'loading…'}
        </div>
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load news: {error}</div>}
      {!error && !data && <div className="mt-4 text-sm text-axe-dim">Loading news…</div>}

      {!error && data && (
        <div className="space-y-4 mt-4">
          {(data.items || []).length === 0 ? (
            <div className="text-sm text-axe-dim">No stories cleared the impact threshold.</div>
          ) : (
            (data.items || []).map((item) => <NewsCard key={item.id} item={item} />)
          )}
        </div>
      )}
    </section>
  )
}
