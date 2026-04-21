import React, { useState } from 'react'
import DecisionInbox from './command-center/DecisionInbox'
import LiveMissionBoard from './command-center/LiveMissionBoard'
import FirmExceptions from './command-center/FirmExceptions'
import WatcherGrid from './command-center/WatcherGrid'
import SurveillanceBoard from './command-center/SurveillanceBoard'
import MissionTakeover from './command-center/MissionTakeover'

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
          <DecisionInbox items={payload.decision_inbox} />
        </div>
        <div className="xl:col-span-5">
          <LiveMissionBoard
            missions={payload.live_missions}
            selectedRunId={selectedRunId}
            onSelect={setSelectedRunId}
          />
        </div>
        <div className="xl:col-span-3">
          <FirmExceptions items={payload.firm_exceptions} />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5">
        <div className="xl:col-span-4">
          <WatcherGrid items={payload.watchers} />
        </div>
        <div className="xl:col-span-8">
          <SurveillanceBoard items={payload.surveillance_alerts} />
        </div>
      </div>

      {selectedMission && <MissionTakeover mission={selectedMission} />}
    </div>
  )
}
