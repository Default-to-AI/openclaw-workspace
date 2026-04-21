function bust(path, now = () => Date.now()) {
  const sep = path.includes('?') ? '&' : '?'
  return `${path}${sep}_=${now()}`
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: 'no-store' })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  return response.json()
}

export async function loadCommandCenter(now = () => Date.now()) {
  try {
    return await fetchJson(bust('/api/command-center', now))
  } catch {
    return fetchJson(bust('/command-center.json', now))
  }
}

function isNewer(nextValue, currentValue) {
  if (!currentValue) return true
  if (!nextValue) return false
  return nextValue >= currentValue
}

export function mergeMissionEvent(state, event) {
  if (!event?.run_id) return state

  let focus = state.current_focus
  const liveMissions = (state.live_missions || []).map((mission) => {
    if (mission.run_id !== event.run_id) {
      return mission
    }
    if (!isNewer(event.updated_at, mission.updated_at)) {
      return mission
    }
    return { ...mission, ...event }
  })

  if (focus?.run_id === event.run_id && isNewer(event.updated_at, focus.updated_at)) {
    focus = { ...focus, ...event }
  }

  return {
    ...state,
    live_missions: liveMissions,
    current_focus: focus,
  }
}
