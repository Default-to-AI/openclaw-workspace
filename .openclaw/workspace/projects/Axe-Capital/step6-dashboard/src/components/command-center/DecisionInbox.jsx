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

export default function DecisionInbox({ items }) {
  return (
    <section className="panel-card">
      <div className="panel-header">
        <div className="panel-title">Decision Inbox</div>
      </div>
      <div className="mt-4">
        {items?.length ? (
          <div className="space-y-3">
            {items.map((item) => (
              <div key={item.run_id || item.symbol} className="rounded-lg border border-axe-border p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-lg font-semibold text-axe-text">{item.symbol}</div>
                    <div className="mt-1 text-sm text-axe-dim">{item.summary}</div>
                  </div>
                  <span className={`ui-badge ${toneForStatus(item.action)}`}>{item.action}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-axe-border p-4 text-sm text-axe-dim">
            <div className="text-axe-text font-medium">No decisions need review</div>
            <div className="mt-1">The firm is quiet for now. Check History if you want recent conclusions.</div>
          </div>
        )}
      </div>
    </section>
  )
}
