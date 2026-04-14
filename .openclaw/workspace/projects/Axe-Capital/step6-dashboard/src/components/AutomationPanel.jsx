import { useEffect, useState } from 'react'

function Badge({ label, className = '' }) {
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-full border border-axe-border bg-axe-muted/20 text-axe-dim ${className}`}>
      {label}
    </span>
  )
}

function Item({ title, ok, note }) {
  return (
    <div className="flex items-start justify-between gap-4 py-3 border-b border-axe-border/40 last:border-b-0">
      <div>
        <div className="text-axe-text text-sm font-medium">{title}</div>
        {note && <div className="text-axe-dim text-xs mt-0.5">{note}</div>}
      </div>
      <Badge
        label={ok ? 'OK' : 'MISSING'}
        className={ok ? 'text-emerald-300 border-emerald-800/60 bg-emerald-900/10' : 'text-axe-red border-red-800/60 bg-red-900/20'}
      />
    </div>
  )
}

export default function AutomationPanel() {
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [files, setFiles] = useState({})

  useEffect(() => {
    // Phase 1: just check if expected static artifacts exist in public/
    const checks = [
      ['portfolio.json', '/portfolio.json'],
      ['targets.json', '/targets.json'],
      ['weekly-review-latest.json', '/weekly-review-latest.json'],
      ['approval-queue.md', '/approval-queue.md'],
      ['decision-log.jsonl', '/decision-log.jsonl'],
      ['health.json', '/health.json'],
    ]

    Promise.all(
      checks.map(([name, url]) =>
        fetch(url, { method: 'GET' })
          .then((r) => ({ name, ok: r.ok, status: r.status }))
          .catch(() => ({ name, ok: false, status: 'ERR' }))
      )
    )
      .then((results) => {
        const map = {}
        for (const r of results) map[r.name] = r
        setFiles(map)
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-axe-dim text-sm">
        Loading automation status...
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

  const okCount = Object.values(files).filter((f) => f.ok).length
  const total = Object.keys(files).length

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-axe-text font-semibold text-base tracking-wide">
            Panel 6 — Automation
          </h2>
          <p className="text-axe-dim text-xs mt-0.5">
            Pipeline artifact presence checks (phase 1: static files)
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <Badge label={`${okCount}/${total} present`} />
        </div>
      </div>

      <div className="bg-axe-surface border border-axe-border rounded-lg p-4">
        <Item title="portfolio.json" ok={!!files['portfolio.json']?.ok} note="From step5 tracker → dashboard" />
        <Item title="targets.json" ok={!!files['targets.json']?.ok} note="Rules for stops/targets" />
        <Item title="weekly-review-latest.json" ok={!!files['weekly-review-latest.json']?.ok} note="From step5 tracker reports" />
        <Item title="approval-queue.md" ok={!!files['approval-queue.md']?.ok} note="Proposed trades pending approval" />
        <Item title="decision-log.jsonl" ok={!!files['decision-log.jsonl']?.ok} note="Audit trail of pipeline events" />
        <Item title="health.json" ok={!!files['health.json']?.ok} note="Automation heartbeat status" />
      </div>

      <div className="text-axe-dim text-xs">
        Next step: generate these artifacts automatically via cron and copy into <span className="text-axe-text">public/</span>.
      </div>
    </div>
  )
}

