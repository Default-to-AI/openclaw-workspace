import { useEffect, useMemo, useState } from 'react'
import { fetchTextWithFallback, describeError } from '../lib/api'

function parseJsonl(text) {
  return text
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line)
      } catch {
        return null
      }
    })
    .filter(Boolean)
}

function normalizeEntry(entry, index) {
  return {
    id: `${entry.run_id || entry.ts || entry.timestamp || index}`,
    ts: entry.ts || entry.timestamp || null,
    ticker: entry.ticker || entry.symbol || '—',
    decisionType: entry.decision_type || entry.type || entry.event || 'note',
    action: entry.action || entry.decision || '—',
    note: entry.note || entry.summary || entry.reason || '',
    tags: entry.tags || [],
    runId: entry.run_id || null,
  }
}

function formatTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

export default function DecisionArchivePanel({ onOpenTrace = () => {} }) {
  const [entries, setEntries] = useState([])
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')

  useEffect(() => {
    let cancelled = false
    fetchTextWithFallback({ filePath: '/decision-log.jsonl' })
      .then((text) => {
        if (cancelled) return
        const parsed = parseJsonl(text).map(normalizeEntry)
        setEntries(parsed)
      })
      .catch((err) => {
        if (cancelled) return
        setError(describeError(err))
      })
    return () => {
      cancelled = true
    }
  }, [])

  const decisionTypes = useMemo(() => {
    const types = new Set(entries.map((entry) => entry.decisionType))
    return ['all', ...Array.from(types)]
  }, [entries])

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase()
    return [...entries]
      .filter((entry) => (typeFilter === 'all' ? true : entry.decisionType === typeFilter))
      .filter((entry) => {
        if (!term) return true
        return [entry.ticker, entry.decisionType, entry.action, entry.note, ...(entry.tags || [])]
          .join(' ')
          .toLowerCase()
          .includes(term)
      })
      .sort((a, b) => {
        const at = a.ts ? new Date(a.ts).getTime() : 0
        const bt = b.ts ? new Date(b.ts).getTime() : 0
        return bt - at
      })
  }, [entries, query, typeFilter])

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="panel-title">Panel 7 — Decision Archive</div>
          <p className="text-axe-dim text-xs mt-1">
            Searchable archive of decisions, notes, and automation events.
          </p>
        </div>
        <div className="text-axe-dim text-xs">{filtered.length} visible entries</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_220px] gap-3 mt-4">
        <input
          className="ui-input"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Filter by ticker, tag, action, or summary"
        />
        <select className="ui-input" value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
          {decisionTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load decision archive: {error}</div>}

      {!error && (
        <div className="overflow-x-auto mt-4">
          <table className="data-table">
            <thead>
              <tr>
                <th className="pl-4">Time</th>
                <th>Ticker</th>
                <th>Type</th>
                <th>Action</th>
                <th>Tags</th>
                <th>Summary</th>
                <th className="pr-4">Trace</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((entry) => (
                <tr key={entry.id}>
                  <td className="pl-4 text-axe-dim">{formatTime(entry.ts)}</td>
                  <td className="text-axe-text font-semibold">{entry.ticker}</td>
                  <td className="text-axe-dim">{entry.decisionType}</td>
                  <td className="text-axe-dim">{entry.action}</td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {(entry.tags || []).length === 0 ? (
                        <span className="text-axe-dim">—</span>
                      ) : (
                        (entry.tags || []).map((tag) => (
                          <span key={tag} className="ui-badge text-axe-dim border-axe-border bg-axe-muted/20">{tag}</span>
                        ))
                      )}
                    </div>
                  </td>
                  <td className="text-left text-axe-dim max-w-[520px] truncate">{entry.note || '—'}</td>
                  <td className="pr-4">
                    {entry.runId ? (
                      <button className="ui-button-secondary" onClick={() => onOpenTrace(entry.runId)}>
                        Open
                      </button>
                    ) : (
                      <span className="text-axe-dim">—</span>
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="pl-4 pr-4 py-6 text-center text-axe-dim text-xs">
                    No archive entries match this filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
