import { useEffect, useState } from 'react'
import { fetchJsonWithFallback, startCommitteeRun } from '../lib/api'
import LiveCommitteeRoom from './LiveCommitteeRoom'

const CANDIDATE_TYPES = [
  { id: 'position_review', label: 'Position review' },
  { id: 'new_position',    label: 'New position' },
]

export default function CommitteePanel({ refreshToken }) {
  const [positions, setPositions] = useState([])
  const [ticker, setTicker] = useState('')
  const [customTicker, setCustomTicker] = useState('')
  const [candidateType, setCandidateType] = useState('position_review')
  const [running, setRunning] = useState(false)
  const [runId, setRunId] = useState(null)
  const [activeTicker, setActiveTicker] = useState(null)
  const [startError, setStartError] = useState(null)

  useEffect(() => {
    fetchJsonWithFallback({ filePath: '/portfolio.json' })
      .then((d) => {
        const syms = (d?.positions || []).map((p) => p.symbol).filter(Boolean).sort()
        setPositions(syms)
        if (syms.length > 0 && !ticker) setTicker(syms[0])
      })
      .catch(() => {})
  }, [refreshToken])

  const effectiveTicker = ticker === '__custom__' ? customTicker.trim().toUpperCase() : ticker

  async function handleRun() {
    if (!effectiveTicker) return
    setStartError(null)
    setRunning(true)
    setRunId(null)
    setActiveTicker(null)
    try {
      const result = await startCommitteeRun(effectiveTicker, candidateType)
      setRunId(result.run_id)
      setActiveTicker(result.ticker)
    } catch (err) {
      setStartError(err.message)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-5">
      {/* Controls */}
      <div className="rounded-lg border border-axe-border bg-axe-surface p-4">
        <div className="flex items-center justify-between mb-4">
          <span className="text-axe-text text-sm font-medium">Committee Run</span>
          <span className="text-axe-muted text-[11px]">Manual trigger — Phase 1</span>
        </div>

        <div className="flex flex-wrap gap-3 items-end">
          {/* Ticker selector */}
          <div className="flex flex-col gap-1">
            <label className="text-axe-muted text-[10px] uppercase tracking-wide">Ticker</label>
            <select
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              disabled={running}
              className="bg-axe-bg border border-axe-border rounded px-2.5 py-1.5 text-axe-text text-xs focus:outline-none focus:border-axe-accent disabled:opacity-50"
            >
              {positions.map((sym) => (
                <option key={sym} value={sym}>{sym}</option>
              ))}
              <option value="__custom__">Custom…</option>
            </select>
          </div>

          {/* Custom ticker input */}
          {ticker === '__custom__' && (
            <div className="flex flex-col gap-1">
              <label className="text-axe-muted text-[10px] uppercase tracking-wide">Symbol</label>
              <input
                type="text"
                value={customTicker}
                onChange={(e) => setCustomTicker(e.target.value.toUpperCase())}
                placeholder="e.g. NVDA"
                disabled={running}
                className="bg-axe-bg border border-axe-border rounded px-2.5 py-1.5 text-axe-text text-xs w-24 focus:outline-none focus:border-axe-accent disabled:opacity-50"
              />
            </div>
          )}

          {/* Candidate type */}
          <div className="flex flex-col gap-1">
            <label className="text-axe-muted text-[10px] uppercase tracking-wide">Type</label>
            <div className="flex rounded border border-axe-border overflow-hidden">
              {CANDIDATE_TYPES.map((ct) => (
                <button
                  key={ct.id}
                  onClick={() => setCandidateType(ct.id)}
                  disabled={running}
                  className={[
                    'px-3 py-1.5 text-xs transition-all',
                    candidateType === ct.id
                      ? 'bg-axe-accent text-white'
                      : 'bg-axe-bg text-axe-dim hover:text-axe-text hover:bg-white/[0.04]',
                    'disabled:opacity-50',
                  ].join(' ')}
                >
                  {ct.label}
                </button>
              ))}
            </div>
          </div>

          {/* Run button */}
          <button
            onClick={handleRun}
            disabled={running || !effectiveTicker}
            className="px-4 py-1.5 rounded bg-axe-accent text-white text-xs font-medium hover:opacity-90 disabled:opacity-40 transition-opacity"
          >
            {running ? 'Starting…' : 'Run committee'}
          </button>
        </div>

        {startError && (
          <p className="mt-3 text-red-300 text-xs">{startError}</p>
        )}
      </div>

      {/* Live room */}
      {runId && <LiveCommitteeRoom runId={runId} ticker={activeTicker} />}
    </div>
  )
}
