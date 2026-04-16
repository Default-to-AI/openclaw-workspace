import { useEffect, useMemo, useState } from 'react'
import { createTraceStream, fetchJsonWithFallback, describeError } from '../lib/api'

function mergeEventList(existing, nextEvent) {
  const list = existing || []
  if (list.some((event) => event.seq === nextEvent.seq)) {
    return list
  }
  return [...list, nextEvent].sort((a, b) => (a.seq || 0) - (b.seq || 0))
}

function streamTone(state) {
  return {
    live: 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10',
    waiting: 'text-amber-300 border-amber-700/60 bg-amber-900/10',
    connecting: 'text-sky-300 border-sky-700/60 bg-sky-900/10',
    complete: 'text-axe-dim border-axe-border bg-axe-muted/20',
    static: 'text-axe-dim border-axe-border bg-axe-muted/20',
    disconnected: 'text-red-300 border-red-700/60 bg-red-900/10',
  }[state] || 'text-axe-dim border-axe-border bg-axe-muted/20'
}

function EventRow({ event }) {
  return (
    <div className="border-l-2 border-axe-accent/50 pl-4 py-3">
      <div className="flex flex-wrap items-center gap-2 text-xs text-axe-dim">
        <span>#{event.seq}</span>
        <span>{event.t}</span>
        <span className="text-axe-text">{event.step}</span>
        {event.elapsed_ms != null && <span>{event.elapsed_ms} ms</span>}
      </div>
      {event.thought && <p className="text-sm text-axe-text mt-2 leading-6">{event.thought}</p>}
      {event.io && (
        <pre className="mt-2 rounded-lg border border-axe-border bg-axe-bg p-3 text-xs text-axe-text overflow-auto">
          {JSON.stringify(event.io, null, 2)}
        </pre>
      )}
      {event.rejected?.length > 0 && (
        <div className="mt-2 text-xs text-red-300">Rejected: {event.rejected.join(', ')}</div>
      )}
    </div>
  )
}

export default function TraceViewerPanel({ runId }) {
  const [trace, setTrace] = useState(null)
  const [error, setError] = useState(null)
  const [streamState, setStreamState] = useState('static')

  useEffect(() => {
    if (!runId) {
      setTrace(null)
      setError(null)
      setStreamState('static')
      return undefined
    }

    let cancelled = false
    let source = null

    setTrace(null)
    setError(null)
    setStreamState('connecting')

    fetchJsonWithFallback({ filePath: `/traces/${runId}.json` })
      .then((payload) => {
        if (cancelled) return
        setTrace(payload)
      })
      .catch((err) => {
        if (cancelled) return
        if (!String(err.message).includes('404')) {
          setError(describeError(err))
        }
      })

    source = createTraceStream(runId, {
      onOpen: () => {
        if (!cancelled) setStreamState('live')
      },
      onWaiting: () => {
        if (!cancelled) setStreamState('waiting')
      },
      onMeta: (meta) => {
        if (cancelled) return
        setTrace((current) => ({
          ...(current || {}),
          ...meta,
          events: current?.events || [],
        }))
      },
      onEvent: (event) => {
        if (cancelled) return
        setTrace((current) => ({
          ...(current || { run_id: runId, events: [] }),
          events: mergeEventList(current?.events, event),
        }))
      },
      onDone: (payload) => {
        if (cancelled) return
        setStreamState('complete')
        setTrace((current) => ({
          ...(current || {}),
          status: payload.status,
          summary: payload.summary,
          ended_at: payload.ended_at || current?.ended_at,
        }))
      },
      onError: () => {
        if (cancelled) return
        setStreamState((current) => (current === 'live' ? 'disconnected' : 'static'))
      },
    })

    return () => {
      cancelled = true
      source?.close?.()
    }
  }, [runId])

  const events = useMemo(() => trace?.events || [], [trace])

  return (
    <section className="panel-card h-full">
      <div className="panel-header">
        <div>
          <div className="panel-title">Internal Dialogue Viewer</div>
          <p className="text-axe-dim text-xs mt-1">
            Agent trace playback, with live SSE when the API is up.
          </p>
        </div>
        <div className={`ui-badge ${streamTone(streamState)}`}>{streamState}</div>
      </div>

      {!runId && <div className="mt-4 text-sm text-axe-dim">Pick a run from the Agent Status Board.</div>}

      {runId && error && !trace && <div className="mt-4 text-sm text-red-300">Unable to load trace: {error}</div>}

      {runId && !error && !trace && streamState === 'static' && (
        <div className="mt-4 text-sm text-axe-dim">No saved trace found yet, and live trace streaming is unavailable.</div>
      )}

      {runId && (trace || streamState === 'waiting' || streamState === 'connecting') && (
        <div className="mt-4 space-y-4">
          <div className="rounded-lg border border-axe-border bg-axe-bg/30 p-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-axe-text font-semibold">{trace?.agent || 'pending trace'}</span>
              <span className="ui-badge text-axe-dim border-axe-border bg-axe-muted/20">{trace?.status || 'pending'}</span>
              {trace?.run_id && <span className="ui-badge text-axe-dim border-axe-border bg-axe-muted/20">{trace.run_id}</span>}
            </div>
            <div className="text-xs text-axe-dim mt-3">
              {trace?.started_at || 'waiting for run to start'}
              {trace?.ended_at ? ` → ${trace.ended_at}` : ''}
            </div>
            <div className="text-sm text-axe-text mt-3">{trace?.summary || 'Waiting for trace output…'}</div>
          </div>

          <div className="space-y-3 max-h-[640px] overflow-auto pr-1">
            {events.length === 0 ? (
              <div className="text-sm text-axe-dim">No events yet.</div>
            ) : (
              events.map((event) => <EventRow key={event.seq} event={event} />)
            )}
          </div>
        </div>
      )}
    </section>
  )
}
