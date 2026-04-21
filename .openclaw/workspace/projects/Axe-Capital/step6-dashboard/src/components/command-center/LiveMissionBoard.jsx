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

export default function LiveMissionBoard({ missions, selectedRunId, onSelect }) {
  return (
    <section className="panel-card">
      <div className="panel-header">
        <div className="panel-title">Live Mission Board</div>
      </div>
      <div className="mt-4">
        {missions?.length ? (
          <div className="space-y-3">
            {missions.map((mission) => (
              <button
                key={mission.run_id}
                type="button"
                aria-label={`Open mission ${mission.run_id}`}
                onClick={() => onSelect?.(mission.run_id)}
                className="w-full rounded-lg border border-axe-border p-4 text-left transition hover:bg-white/[0.03]"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-axe-text">{mission.run_id}</div>
                    <div className="mt-1 text-sm text-axe-dim">{mission.headline || mission.latest_summary}</div>
                  </div>
                  <span className={`ui-badge ${toneForStatus(mission.status)}`}>{mission.status}</span>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-axe-border p-4 text-sm text-axe-dim">
            <div className="text-axe-text font-medium">No live missions</div>
            <div className="mt-1">No mission is running now. The next completed decision will land in the inbox.</div>
          </div>
        )}
      </div>
    </section>
  )
}
