import React from 'react'

function toneForStatus(status) {
  if (status === 'fresh') return 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
  if (status === 'stale') return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  return 'text-red-300 border-red-700/60 bg-red-900/10'
}

export default function FirmExceptions({ items }) {
  return (
    <section className="panel-card">
      <div className="panel-header">
        <div className="panel-title">Firm Exceptions</div>
      </div>
      <div className="mt-4">
        {items?.length ? (
          <div className="space-y-3">
            {items.map((item) => (
              <div key={item.key} className="rounded-lg border border-axe-border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm text-axe-text">{item.key}</div>
                  <span className={`ui-badge ${toneForStatus(item.status)}`}>{item.status}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-axe-border p-4 text-sm text-axe-dim">
            <div className="text-axe-text font-medium">No critical exceptions</div>
            <div className="mt-1">Health is quiet. This rail stays collapsed when nothing needs intervention.</div>
          </div>
        )}
      </div>
    </section>
  )
}
