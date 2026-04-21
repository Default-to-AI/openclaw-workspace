import { createCommitteeStream } from '../api'

export function subscribeToMission(runId, handlers) {
  if (!runId) return () => {}
  const source = createCommitteeStream(runId, handlers)
  return () => source?.close?.()
}
