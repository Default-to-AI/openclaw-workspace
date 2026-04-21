import { useEffect, useRef, useState } from 'react'
import { createCommitteeStream } from '../lib/api'

const ROLE_META = {
  orchestrator: { label: 'Orchestrator', color: 'text-axe-dim border-axe-border' },
  fundamental:  { label: 'Fundamental', color: 'text-blue-300 border-blue-700/60 bg-blue-900/10' },
  technical:    { label: 'Technical',   color: 'text-cyan-300 border-cyan-700/60 bg-cyan-900/10' },
  macro:        { label: 'Macro',       color: 'text-violet-300 border-violet-700/60 bg-violet-900/10' },
  sentiment:    { label: 'Sentiment',   color: 'text-pink-300 border-pink-700/60 bg-pink-900/10' },
  bull:         { label: 'Bull',        color: 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10' },
  bear:         { label: 'Bear',        color: 'text-red-300 border-red-700/60 bg-red-900/10' },
  debate:       { label: 'Debate',      color: 'text-amber-300 border-amber-700/60 bg-amber-900/10' },
  cro:          { label: 'CRO',         color: 'text-orange-300 border-orange-700/60 bg-orange-900/10' },
  ceo:          { label: 'CEO',         color: 'text-indigo-300 border-indigo-700/60 bg-indigo-900/10' },
  playbook:     { label: 'Playbook',    color: 'text-teal-300 border-teal-700/60 bg-teal-900/10' },
}

const TYPE_LABEL = {
  claim:    'thesis',
  evidence: 'evidence',
  objection: 'risk',
  decision: 'decision',
  error:    'error',
}

function RoleBadge({ role }) {
  const meta = ROLE_META[role] || { label: role, color: 'text-axe-dim border-axe-border' }
  return (
    <span className={`ui-badge text-[10px] uppercase tracking-wide ${meta.color}`}>
      {meta.label}
    </span>
  )
}

function ConfidenceBar({ value }) {
  const pct = Math.round((value ?? 0) * 100)
  const barColor = pct >= 70 ? 'bg-emerald-500' : pct >= 40 ? 'bg-amber-400' : 'bg-red-500'
  return (
    <div className="flex items-center gap-1.5 shrink-0">
      <div className="w-14 h-1 rounded-full bg-white/10 overflow-hidden">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-axe-muted text-[10px] w-6 text-right">{pct}%</span>
    </div>
  )
}

function EventRow({ ev }) {
  const isDecision = ev.event_type === 'decision'
  const isError = ev.event_type === 'error'

  return (
    <div className={[
      'flex items-start gap-2.5 py-2 border-b border-axe-border/40 last:border-0',
      isDecision ? 'bg-indigo-950/20 rounded px-2 -mx-2' : '',
      isError ? 'bg-red-950/20 rounded px-2 -mx-2' : '',
    ].join(' ')}>
      <div className="flex items-center gap-1.5 shrink-0 pt-0.5">
        <RoleBadge role={ev.role} />
        {ev.event_type && (
          <span className="text-axe-muted text-[10px]">
            {TYPE_LABEL[ev.event_type] ?? ev.event_type}
          </span>
        )}
      </div>
      <p className={[
        'flex-1 text-xs leading-relaxed min-w-0',
        isDecision ? 'text-axe-text font-medium' : isError ? 'text-red-300' : 'text-axe-dim',
      ].join(' ')}>
        {ev.content}
      </p>
      <ConfidenceBar value={ev.confidence} />
    </div>
  )
}

function CeoDecisionCard({ ev }) {
  if (!ev) return null
  const action = ev.action || ev.memo?.action || 'WATCH'
  const conviction = ev.memo?.conviction_1_to_10 || ev.memo?.conviction || 5
  const thesis = ev.memo?.thesis || ev.memo?.rationale || ''

  const actionColor = {
    BUY: 'text-emerald-300', ADD: 'text-emerald-300',
    SELL: 'text-red-300', TRIM: 'text-red-300',
    HOLD: 'text-amber-300', WATCH: 'text-axe-dim',
    TIGHTEN_STOP: 'text-orange-300', LOOSEN_STOP: 'text-orange-300',
    REBALANCE: 'text-blue-300',
  }[action] || 'text-axe-dim'

  return (
    <div className="mt-4 rounded-lg border border-indigo-700/40 bg-indigo-950/20 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-axe-muted text-[10px] uppercase tracking-wider">CEO Decision</span>
        <span className="text-axe-dim text-[10px]">conviction {conviction}/10</span>
      </div>
      <div className={`text-2xl font-bold tracking-wide mb-2 ${actionColor}`}>{action}</div>
      {thesis && <p className="text-axe-dim text-xs leading-relaxed">{thesis}</p>}
    </div>
  )
}

const TRIGGER_COLOR = {
  support:    'text-emerald-300',
  resistance: 'text-red-300',
  stop:       'text-red-400',
  target:     'text-blue-300',
}

function PlaybookCard({ ev }) {
  if (!ev?.memo) return null
  const p = ev.memo
  const levels = Array.isArray(p.key_levels) ? p.key_levels : []

  return (
    <div className="mt-4 rounded-lg border border-teal-700/40 bg-teal-950/20 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-axe-muted text-[10px] uppercase tracking-wider">Position Playbook</span>
        <div className="flex gap-2">
          {p.stop_loss_level && (
            <span className="ui-badge text-red-300 border-red-700/60 bg-red-900/10">
              Stop ${Number(p.stop_loss_level).toLocaleString()}
            </span>
          )}
          {p.target_price && (
            <span className="ui-badge text-blue-300 border-blue-700/60 bg-blue-900/10">
              Target ${Number(p.target_price).toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {levels.length > 0 && (
        <div>
          <div className="text-axe-muted text-[10px] uppercase tracking-wider mb-1.5">Key Levels</div>
          <div className="space-y-1">
            {levels.map((lvl, i) => {
              const triggerKey = (lvl.trigger || lvl.label || '').toLowerCase()
              const colorClass = Object.entries(TRIGGER_COLOR).find(([k]) => triggerKey.includes(k))?.[1] || 'text-axe-dim'
              return (
                <div key={i} className="flex items-start gap-2.5 py-1 border-b border-axe-border/30 last:border-0">
                  <span className={`text-xs font-mono font-medium shrink-0 w-20 ${colorClass}`}>
                    ${Number(lvl.price).toLocaleString()}
                  </span>
                  <span className="text-axe-dim text-[11px] flex-1">{lvl.label}</span>
                  <span className="text-axe-text text-[11px] font-medium shrink-0">{lvl.action}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-2 text-xs">
        {p.if_price_rises && (
          <div className="flex gap-2">
            <span className="text-emerald-400 shrink-0">↑</span>
            <span className="text-axe-dim leading-relaxed">{p.if_price_rises}</span>
          </div>
        )}
        {p.if_price_falls && (
          <div className="flex gap-2">
            <span className="text-red-400 shrink-0">↓</span>
            <span className="text-axe-dim leading-relaxed">{p.if_price_falls}</span>
          </div>
        )}
        {p.if_sideways && (
          <div className="flex gap-2">
            <span className="text-axe-muted shrink-0">→</span>
            <span className="text-axe-dim leading-relaxed">{p.if_sideways}</span>
          </div>
        )}
      </div>

      {(p.review_trigger || p.sizing_note) && (
        <div className="space-y-1 border-t border-teal-700/20 pt-3">
          {p.review_trigger && (
            <p className="text-axe-muted text-[11px]">
              <span className="text-axe-dim">Review when:</span> {p.review_trigger}
            </p>
          )}
          {p.sizing_note && (
            <p className="text-axe-muted text-[11px]">
              <span className="text-axe-dim">Sizing:</span> {p.sizing_note}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default function LiveCommitteeRoom({ runId, ticker }) {
  const [events, setEvents] = useState([])
  const [done, setDone] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)
  const ceoDecision = events.find((e) => e.event_type === 'decision' && e.role === 'ceo') || null
  const playbookEvent = events.find((e) => e.event_type === 'playbook' && e.role === 'playbook') || null

  useEffect(() => {
    if (!runId) return
    setEvents([])
    setDone(false)
    setError(null)

    const source = createCommitteeStream(runId, {
      onEvent: (ev) => setEvents((prev) => [...prev, ev]),
      onDone: () => setDone(true),
      onError: (err) => setError(err.message),
    })

    return () => source?.close()
  }, [runId])

  useEffect(() => {
    if (events.length > 0) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [events.length])

  if (!runId) return null

  return (
    <div className="rounded-lg border border-axe-border bg-axe-surface">
      <div className="flex items-center justify-between px-4 py-3 border-b border-axe-border">
        <div className="flex items-center gap-2">
          <span className="text-axe-text text-sm font-medium">Committee Room</span>
          {ticker && <span className="ui-badge text-axe-accent border-axe-accent/40 bg-axe-accent/10">{ticker}</span>}
        </div>
        <div className="flex items-center gap-2">
          {!done && !error && (
            <span className="flex items-center gap-1.5 text-axe-muted text-[11px]">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              running
            </span>
          )}
          {done && <span className="ui-badge text-emerald-300 border-emerald-700/60 bg-emerald-900/10">complete</span>}
          {error && <span className="ui-badge text-red-300 border-red-700/60 bg-red-900/10">error</span>}
        </div>
      </div>

      <div className="px-4 py-3 max-h-[520px] overflow-y-auto space-y-0">
        {events.length === 0 && !error && (
          <p className="text-axe-muted text-xs py-4 text-center">Waiting for first event…</p>
        )}
        {events.map((ev, i) => (
          <EventRow key={i} ev={ev} />
        ))}
        {error && (
          <div className="py-4 text-red-300 text-xs text-center">{error}</div>
        )}
        <div ref={bottomRef} />
      </div>

      {(ceoDecision || playbookEvent) && (
        <div className="px-4 pb-4 space-y-0">
          {ceoDecision && <CeoDecisionCard ev={ceoDecision} />}
          {playbookEvent && <PlaybookCard ev={playbookEvent} />}
        </div>
      )}
    </div>
  )
}
