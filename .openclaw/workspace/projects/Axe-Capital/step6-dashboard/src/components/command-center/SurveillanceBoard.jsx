import React from 'react'

function toneForStatus(status) {
  if (status === 'fresh' || status === 'running' || status === 'completed') {
    return 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
  }
  if (status === 'stale' || status === 'queued' || status === 'blocked') {
    return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  }
  if (status === 'failed' || status === 'missing' || status === 'RED') {
    return 'text-red-300 border-red-700/60 bg-red-900/10'
  }
  return 'text-axe-dim border-axe-border'
}

export default function SurveillanceBoard({ items }) {
  return (
    <section className="panel-card">
      <div className="panel-header">
        <div className="panel-title">Portfolio Surveillance Board</div>
      </div>
      <div className="mt-4">
        {items?.length ? (
          <div className="space-y-3">
            {items.map((alert) => (
              <div key={alert.symbol} className="rounded-lg border border-axe-border p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-axe-text">{alert.symbol}</div>
                    <div className="mt-1 text-sm text-axe-dim">{alert.thesis || 'No thesis attached yet.'}</div>
                  </div>
                  <span className={`ui-badge ${toneForStatus(alert.severity)}`}>{alert.severity}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-axe-border p-4 text-sm text-axe-dim">
            <div className="text-axe-text font-medium">No portfolio exceptions</div>
            <div className="mt-1">Surveillance is clean right now.</div>
          </div>
        )}
      </div>
    </section>
  )
}
