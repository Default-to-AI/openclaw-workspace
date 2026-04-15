async function parseResponse(response, parser) {
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  return parser(response)
}

async function tryFetch(path, parser) {
  const response = await fetch(path)
  return parseResponse(response, parser)
}

export async function fetchJsonWithFallback({ apiPath, filePath }) {
  let lastError = null

  if (apiPath) {
    try {
      return await tryFetch(apiPath, (response) => response.json())
    } catch (error) {
      lastError = error
    }
  }

  if (filePath) {
    try {
      return await tryFetch(filePath, (response) => response.json())
    } catch (error) {
      lastError = error
    }
  }

  throw lastError || new Error('Unable to load JSON artifact')
}

export async function fetchTextWithFallback({ apiPath, filePath }) {
  let lastError = null

  if (apiPath) {
    try {
      return await tryFetch(apiPath, (response) => response.text())
    } catch (error) {
      lastError = error
    }
  }

  if (filePath) {
    try {
      return await tryFetch(filePath, (response) => response.text())
    } catch (error) {
      lastError = error
    }
  }

  throw lastError || new Error('Unable to load text artifact')
}

export async function fetchHealthStatus() {
  try {
    const data = await tryFetch('/api/health', (response) => response.json())
    return { data, source: 'api' }
  } catch {
    const data = await tryFetch('/health.json', (response) => response.json())
    return { data, source: 'file' }
  }
}

export async function fetchHealth() {
  const { data } = await fetchHealthStatus()
  return data
}

export async function triggerRefresh(target) {
  const response = await fetch(`/api/refresh/${encodeURIComponent(target)}`, {
    method: 'POST',
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const payload = await response.json()
      detail = payload.detail || detail
    } catch {
      // ignore, keep generic detail
    }
    throw new Error(detail)
  }

  return response.json()
}

function parseEventData(event) {
  try {
    return JSON.parse(event.data)
  } catch {
    return event.data
  }
}

export function createTraceStream(runId, handlers = {}) {
  if (typeof EventSource === 'undefined') {
    return null
  }

  const source = new EventSource(`/api/trace/stream/${encodeURIComponent(runId)}`)
  let opened = false

  source.onopen = () => {
    opened = true
    handlers.onOpen?.()
  }

  source.addEventListener('waiting', (event) => {
    handlers.onWaiting?.(parseEventData(event))
  })

  source.addEventListener('meta', (event) => {
    opened = true
    handlers.onMeta?.(parseEventData(event))
  })

  source.addEventListener('event', (event) => {
    opened = true
    handlers.onEvent?.(parseEventData(event))
  })

  source.addEventListener('done', (event) => {
    opened = true
    handlers.onDone?.(parseEventData(event))
    source.close()
  })

  source.onerror = () => {
    handlers.onError?.(
      new Error(opened ? 'Trace stream disconnected' : 'Trace stream unavailable')
    )
    if (!opened) {
      source.close()
    }
  }

  return source
}
