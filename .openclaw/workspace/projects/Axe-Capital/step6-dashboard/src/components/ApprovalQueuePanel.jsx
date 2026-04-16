import { useEffect, useState } from 'react'
import { fetchTextWithFallback, describeError } from '../lib/api'

function parseApprovalQueue(text) {
  const lines = text.split('\n')
  const sections = { pending: [], approved: [], rejected: [] }
  let current = null

  for (const raw of lines) {
    const line = raw.trim()
    if (line.startsWith('## Pending')) { current = 'pending'; continue }
    if (line.startsWith('## Approved')) { current = 'approved'; continue }
    if (line.startsWith('## Rejected')) { current = 'rejected'; continue }
    if (!current || !line.startsWith('|') || line.startsWith('|---')) continue
    if (line.includes('Date') && line.includes('Ticker')) continue // header row

    const cells = line.split('|').map((c) => c.trim()).filter(Boolean)
    if (cells.length < 4) continue

    const [date, ticker, action, size, thesis = '', invalidation = '', logLink = ''] = cells
    if (!ticker || !action) continue

    sections[current].push({ date, ticker, action, size, thesis, invalidation, logLink })
  }

  return sections
}

function actionTone(action) {
  if (action === 'BUY') return 'text-emerald-400 font-bold'
  if (action === 'SELL') return 'text-red-400 font-bold'
  if (action === 'HOLD') return 'text-amber-400 font-bold'
  return 'text-axe-dim'
}

function QueueRow({ item }) {
  return (
    <div className="px-4 py-3 border-b border-axe-border last:border-b-0 flex items-start justify-between gap-4">
      <div className="flex-1 min-w-0 space-y-1.5">
        <div className="flex flex-wrap items-center gap-2.5">
          <span className={`text-sm ${actionTone(item.action)}`}>{item.action}</span>
          <span className="font-bold text-axe-text">{item.ticker}</span>
          <span className="text-axe-dim text-xs">{item.date}</span>
          {item.size && (
            <span className="ui-badge text-axe-dim border-axe-border">{item.size}</span>
          )}
        </div>
        {item.thesis && (
          <div className="text-xs text-axe-text leading-relaxed">{item.thesis}</div>
        )}
        {item.invalidation && (
          <div className="text-[11px] text-axe-dim">{item.invalidation}</div>
        )}
      </div>
      <div className="flex flex-col gap-1.5 flex-shrink-0">
        <span className="ui-badge text-axe-dim border-axe-border text-[10px]">
          Manual sign-off required
        </span>
      </div>
    </div>
  )
}

export default function ApprovalQueuePanel({ refreshToken }) {
  const [sections, setSections] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setSections(null)
    setError(null)
    fetchTextWithFallback({ filePath: '/approval-queue.md' })
      .then((text) => {
        if (cancelled) return
        setSections(parseApprovalQueue(text))
      })
      .catch((err) => {
        if (cancelled) return
        setError(describeError(err))
      })
    return () => { cancelled = true }
  }, [refreshToken])

  const pending = sections?.pending ?? []
  const approved = sections?.approved ?? []

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="panel-title">Approval Queue</div>
          <p className="text-axe-dim text-xs mt-1">
            CEO decisions awaiting manual sign-off · approval-queue.md
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className={`ui-badge ${pending.length > 0 ? 'text-amber-300 border-amber-700/60 bg-amber-900/10' : 'text-axe-dim border-axe-border'}`}>
            {pending.length} pending
          </span>
          <span className="ui-badge text-axe-dim border-axe-border">{approved.length} approved</span>
        </div>
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load approval queue: {error}</div>}

      {sections && (
        <div className="mt-4 space-y-4">
          <div>
            <div className="text-axe-dim text-[11px] uppercase tracking-wider mb-2">Pending</div>
            {pending.length === 0 ? (
              <div className="text-axe-dim text-xs py-3 border border-axe-border rounded-lg text-center">
                No pending approvals. Decisions appear here after running the decision agent.
              </div>
            ) : (
              <div className="bg-axe-bg/30 border border-axe-border rounded-lg overflow-hidden">
                {pending.map((item, i) => <QueueRow key={i} item={item} />)}
              </div>
            )}
          </div>

          {approved.length > 0 && (
            <div>
              <div className="text-axe-dim text-[11px] uppercase tracking-wider mb-2">Approved / Executed</div>
              <div className="bg-axe-bg/30 border border-axe-border rounded-lg overflow-hidden">
                {approved.map((item, i) => <QueueRow key={i} item={item} />)}
              </div>
            </div>
          )}

          {approved.length === 0 && (
            <div>
              <div className="text-axe-dim text-[11px] uppercase tracking-wider mb-2">Approved / Executed</div>
              <div className="text-axe-dim text-xs py-3 text-center">No approved orders yet.</div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
