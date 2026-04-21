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

export default function MissionTakeover({ mission }) {
  if (!mission) return null

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div className="panel-title">Mission Takeover</div>
        {mission.status && (
          <span className={`ui-badge ${toneForStatus(mission.status)}`}>{mission.status}</span>
        )}
      </div>
      <div className="mt-4 space-y-3">
        {mission.stream_error && (
          <div className="ui-badge text-red-300 border-red-700/60 bg-red-900/10">
            {mission.stream_error}
          </div>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div className="rounded-lg border border-axe-border p-4">
            <div className="text-xs uppercase tracking-wider text-axe-dim">Mission</div>
            <div className="mt-2 text-lg font-semibold text-axe-text">{mission.run_id}</div>
            <div className="mt-2 text-sm text-axe-dim">{mission.headline || mission.latest_summary}</div>
          </div>
          <div className="rounded-lg border border-axe-border p-4">
            <div className="text-xs uppercase tracking-wider text-axe-dim">Latest Summary</div>
            <div className="mt-2 text-sm text-axe-text">{mission.latest_summary}</div>
            {mission.updated_at && (
              <div className="mt-2 text-xs text-axe-dim">{mission.updated_at}</div>
            )}
          </div>
        </div>
        {mission.evidence_links?.length > 0 && (
          <div className="rounded-lg border border-axe-border p-4">
            <div className="text-xs uppercase tracking-wider text-axe-dim mb-2">Evidence</div>
            <div className="space-y-1">
              {mission.evidence_links.map((link) => (
                <div key={link.label} className="text-sm text-axe-dim">{link.label}</div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
