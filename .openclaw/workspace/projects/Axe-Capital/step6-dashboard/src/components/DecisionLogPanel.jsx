import { useEffect, useMemo, useState } from 'react'

function Badge({ label, className = '' }) {
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-full border border-axe-border bg-axe-muted/20 text-axe-dim ${className}`}>
      {label}
    </span>
  )
}

function parseJsonl(text) {
  const lines = text.split(/\r?\n/).filter(Boolean)
  const out = []
  for (const line of lines) {
    try {
      out.push(JSON.parse(line))
    } catch {
      // skip
    }
  }
  return out
}

export default function DecisionLogPanel() {
  const [entries, setEntries] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/decision-log.jsonl')
      .then((r) => {
        if (!r.ok) throw new Error(`decision-log HTTP ${r.status}`)
        return r.text()
      })
      .then((t) => {
        const parsed = parseJsonl(t)
        setEntries(parsed)
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [])

  const latest = useMemo(() => {
    const rows = [...entries]
    rows.sort((a, b) => {
      const ta = a.ts ?? a.timestamp ?? 0
      const tb = b.ts ?? b.timestamp ?? 0
      return tb - ta
    })
    return rows.slice(0, 20)
  }, [entries])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-axe-dim text-sm">
        Loading decision log...
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

  const count = entries.length

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-axe-text font-semibold text-base tracking-wide">
            Panel 5 — Decision Log
          </h2>
          <p className="text-axe-dim text-xs mt-0.5">
            Latest agent decisions and approvals (jsonl)
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <Badge label={`${count} events`} />
          <Badge label="last 20" />
        </div>
      </div>

      <div className="bg-axe-surface border border-axe-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th className="pl-4">Time</th>
                <th>Type</th>
                <th>Symbol</th>
                <th>Action</th>
                <th className="pr-4">Summary</th>
              </tr>
            </thead>
            <tbody>
              {latest.map((e, idx) => {
                const ts = e.ts ?? e.timestamp ?? null
                const time = ts ? new Date(ts).toLocaleString() : '—'
                const type = e.type ?? e.event ?? 'event'
                const symbol = e.symbol ?? e.ticker ?? '—'
                const action = e.action ?? e.decision ?? '—'
                const summary = e.summary ?? e.note ?? e.reason ?? ''
                return (
                  <tr key={idx}>
                    <td className="pl-4 text-axe-dim">{time}</td>
                    <td className="text-axe-text">{type}</td>
                    <td className="text-axe-text font-semibold">{symbol}</td>
                    <td className="text-axe-dim">{action}</td>
                    <td className="pr-4 text-left text-axe-dim max-w-[520px] truncate">{summary || '—'}</td>
                  </tr>
                )
              })}
              {latest.length === 0 && (
                <tr>
                  <td colSpan={5} className="pl-4 pr-4 py-6 text-center text-axe-dim text-xs">
                    No events yet. Automation will generate decision-log.jsonl.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="text-axe-dim text-xs">
        Source: <span className="text-axe-text">public/decision-log.jsonl</span>
      </div>
    </div>
  )
}

