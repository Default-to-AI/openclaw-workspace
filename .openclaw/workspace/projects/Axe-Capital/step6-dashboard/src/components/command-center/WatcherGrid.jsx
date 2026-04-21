import React from 'react'

function toneForStatus(status) {
  if (status === 'fresh') return 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
  if (status === 'stale') return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  return 'text-red-300 border-red-700/60 bg-red-900/10'
}

export default function WatcherGrid({ items }) {
  return (
    <section className="panel-card">
      <div className="panel-header">
        <div className="panel-title">Autonomous Watcher Grid</div>
      </div>
      <div className="mt-4">
        <div className="space-y-3">
          {(items || []).map((watcher) => (
            <div key={watcher.key} className="rounded-lg border border-axe-border p-3">
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm text-axe-text">{watcher.label}</div>
                <span className={`ui-badge ${toneForStatus(watcher.status)}`}>{watcher.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
