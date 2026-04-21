import React, { useState } from 'react'

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

function EmptyState({ title, body }) {
  return (
    <div className="rounded-lg border border-dashed border-axe-border p-4 text-sm text-axe-dim">
      <div className="text-axe-text font-medium">{title}</div>
      <div className="mt-1">{body}</div>
    </div>
  )
}

function SectionCard({ title, children, aside }) {
  return (
    <section className="panel-card">
      <div className="panel-header">
        <div className="panel-title">{title}</div>
        {aside}
      </div>
      <div className="mt-4">{children}</div>
    </section>
  )
}

export default function CommandCenter({ payload }) {
  const [selectedRunId, setSelectedRunId] = useState(payload?.current_focus?.run_id || null)

  if (!payload) {
    return <div className="text-sm text-axe-dim">Loading command center…</div>
  }

  const selectedMission = payload.live_missions?.find((mission) => mission.run_id === selectedRunId) || null

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-axe-text">Command Center</h1>
          <p className="mt-1 text-sm text-axe-dim">
            Decision-first operator seat for live missions, surveillance, and true exceptions.
          </p>
        </div>
        {payload.partial && (
          <span className="ui-badge text-amber-300 border-amber-700/60 bg-amber-900/10">
            partial data
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5">
        <div className="xl:col-span-4">
          <SectionCard title="Decision Inbox">
            {payload.decision_inbox?.length ? (
              <div className="space-y-3">
                {payload.decision_inbox.map((item) => (
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
              <EmptyState title="No decisions need review" body="The firm is quiet for now. Check History if you want recent conclusions." />
            )}
          </SectionCard>
        </div>

        <div className="xl:col-span-5">
          <SectionCard title="Live Mission Board">
            {payload.live_missions?.length ? (
              <div className="space-y-3">
                {payload.live_missions.map((mission) => (
                  <button
                    key={mission.run_id}
                    type="button"
                    aria-label={`Open mission ${mission.run_id}`}
                    onClick={() => setSelectedRunId(mission.run_id)}
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
              <EmptyState title="No live missions" body="No mission is running now. The next completed decision will land in the inbox." />
            )}
          </SectionCard>
        </div>

        <div className="xl:col-span-3">
          <SectionCard title="Firm Exceptions">
            {payload.firm_exceptions?.length ? (
              <div className="space-y-3">
                {payload.firm_exceptions.map((item) => (
                  <div key={item.key} className="rounded-lg border border-axe-border p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm text-axe-text">{item.key}</div>
                      <span className={`ui-badge ${toneForStatus(item.status)}`}>{item.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No critical exceptions" body="Health is quiet. This rail stays collapsed when nothing needs intervention." />
            )}
          </SectionCard>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5">
        <div className="xl:col-span-4">
          <SectionCard title="Autonomous Watcher Grid">
            <div className="space-y-3">
              {(payload.watchers || []).map((watcher) => (
                <div key={watcher.key} className="rounded-lg border border-axe-border p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-sm text-axe-text">{watcher.label}</div>
                    <span className={`ui-badge ${toneForStatus(watcher.status)}`}>{watcher.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-8">
          <SectionCard title="Portfolio Surveillance Board">
            {payload.surveillance_alerts?.length ? (
              <div className="space-y-3">
                {payload.surveillance_alerts.map((alert) => (
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
              <EmptyState title="No portfolio exceptions" body="Surveillance is clean right now." />
            )}
          </SectionCard>
        </div>
      </div>

      {selectedMission && (
        <SectionCard
          title="Mission Takeover"
          aside={<span className={`ui-badge ${toneForStatus(selectedMission.status)}`}>{selectedMission.status}</span>}
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="rounded-lg border border-axe-border p-4">
              <div className="text-xs uppercase tracking-wider text-axe-dim">Mission</div>
              <div className="mt-2 text-lg font-semibold text-axe-text">{selectedMission.run_id}</div>
              <div className="mt-2 text-sm text-axe-dim">{selectedMission.headline || selectedMission.latest_summary}</div>
            </div>
            <div className="rounded-lg border border-axe-border p-4">
              <div className="text-xs uppercase tracking-wider text-axe-dim">Latest Summary</div>
              <div className="mt-2 text-sm text-axe-text">{selectedMission.latest_summary}</div>
            </div>
          </div>
        </SectionCard>
      )}
    </div>
  )
}
