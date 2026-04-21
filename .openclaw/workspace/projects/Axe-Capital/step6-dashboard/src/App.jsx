import { useEffect, useState } from 'react'
import './index.css'
import AppSidebar from './components/AppSidebar'
import PortfolioPanel from './components/PortfolioPanel'
import TargetsPanel from './components/TargetsPanel'
import AlphaPanel from './components/AlphaPanel'
import NewsPanel from './components/NewsPanel'
import AgentStatusPanel from './components/AgentStatusPanel'
import TraceViewerPanel from './components/TraceViewerPanel'
import DecisionArchivePanel from './components/DecisionArchivePanel'
import DecisionReportPanel from './components/DecisionReportPanel'
import AnalystReportsPanel from './components/AnalystReportsPanel'
import WeeklyReviewPanel from './components/WeeklyReviewPanel'
import ApprovalQueuePanel from './components/ApprovalQueuePanel'
import CommitteePanel from './components/CommitteePanel'
import CommandCenter from './components/CommandCenter'
import { fetchHealthStatus, fetchJsonWithFallback, fetchTextWithFallback } from './lib/api'
import { loadCommandCenter, mergeMissionEvent } from './lib/command-center/store'
import { subscribeToMission } from './lib/command-center/stream'

const TAB_LABELS = {
  overview: 'Command Center',
  portfolio: 'Portfolio',
  research: 'Research',
  ops: 'Operations',
  committee: 'Committee Room',
}

function actionTone(action) {
  if (action === 'BUY') return 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
  if (action === 'SELL') return 'text-red-300 border-red-700/60 bg-red-900/10'
  if (action === 'HOLD') return 'text-amber-300 border-amber-700/60 bg-amber-900/10'
  return 'text-axe-dim border-axe-border'
}

function FreshnessHeader({ health }) {
  const a = health?.artifacts
  if (!a) return null

  function chip(key, shortLabel) {
    const art = a[key]
    if (!art) return null
    const tone =
      art.status === 'fresh'
        ? 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
        : art.status === 'stale'
          ? 'text-amber-300 border-amber-700/60 bg-amber-900/10'
          : 'text-red-300 border-red-700/60 bg-red-900/10'
    const age = art.age_min != null ? ` · ${art.age_min}m` : ''
    return (
      <span key={key} className={`ui-badge ${tone}`}>
        {shortLabel}: {art.status}{age}
      </span>
    )
  }

  return (
    <div className="hidden lg:flex items-center gap-1.5 flex-wrap">
      {chip('portfolio', 'portfolio')}
      {chip('alpha', 'alpha')}
      {chip('news', 'news')}
      {chip('decision', 'decision')}
    </div>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [activeRunId, setActiveRunId] = useState(null)
  const [refreshToken, setRefreshToken] = useState(0)
  const [health, setHealth] = useState(null)
  const [navBadges, setNavBadges] = useState({})
  const [commandCenter, setCommandCenter] = useState(null)
  const [commandCenterError, setCommandCenterError] = useState(null)

  // Reload health on each refresh
  useEffect(() => {
    let cancelled = false
    fetchHealthStatus()
      .then(({ data }) => { if (!cancelled) setHealth(data) })
      .catch(() => {})
    return () => { cancelled = true }
  }, [refreshToken])

  useEffect(() => {
    let cancelled = false
    loadCommandCenter()
      .then((payload) => {
        if (cancelled) return
        setCommandCenter(payload)
        setCommandCenterError(null)
      })
      .catch((error) => {
        if (cancelled) return
        setCommandCenter(null)
        setCommandCenterError(error.message)
      })
    return () => { cancelled = true }
  }, [refreshToken])

  // Derive nav badges from artifacts
  useEffect(() => {
    let cancelled = false

    fetchJsonWithFallback({ filePath: '/decision-latest.json' })
      .then((d) => {
        if (cancelled) return
        const action = d?.ceo?.action
        if (action && action !== 'PASS') {
          setNavBadges((prev) => ({ ...prev, overview: { label: action, tone: actionTone(action) } }))
        }
      })
      .catch(() => {})

    fetchJsonWithFallback({ filePath: '/portfolio.json' })
      .then((d) => {
        if (cancelled) return
        const red = d?.summary?.red_count ?? 0
        if (red > 0) {
          setNavBadges((prev) => ({
            ...prev,
            overview: prev.overview,
            portfolio: { label: `${red} RED`, tone: 'text-red-300 border-red-700/60 bg-red-900/10' },
          }))
        }
      })
      .catch(() => {})

    fetchTextWithFallback({ filePath: '/approval-queue.md' })
      .then((text) => {
        if (cancelled) return
        const lines = text.split('\n')
        const sepIdx = lines.findIndex((l) => l.trimStart().startsWith('|---'))
        let count = 0
        if (sepIdx >= 0) {
          for (let i = sepIdx + 1; i < lines.length; i++) {
            const l = lines[i].trim()
            if (!l || l.startsWith('#')) break
            if (l.startsWith('|') && l.length > 10) count++
          }
        }
        if (count > 0) {
          setNavBadges((prev) => ({
            ...prev,
            ops: { label: `${count} pending`, tone: 'text-amber-300 border-amber-700/60 bg-amber-900/10' },
          }))
        }
      })
      .catch(() => {})

    return () => { cancelled = true }
  }, [refreshToken])

  useEffect(() => {
    if (!commandCenter?.current_focus?.run_id) return
    return subscribeToMission(commandCenter.current_focus.run_id, {
      onEvent(event) {
        setCommandCenter((current) => mergeMissionEvent(current, event))
      },
      onError(error) {
        setCommandCenter((current) => mergeMissionEvent(current, {
          run_id: current?.current_focus?.run_id,
          stream_error: error.message,
          updated_at: new Date().toISOString(),
        }))
      },
    })
  }, [commandCenter?.current_focus?.run_id])

  function handleRefreshComplete() {
    setRefreshToken((v) => v + 1)
    setNavBadges({})
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* ── Header ── */}
      <header className="flex-shrink-0 h-[52px] flex items-center border-b border-axe-border bg-axe-surface/95 backdrop-blur z-50">
        <div className="w-[140px] sm:w-[210px] flex-shrink-0 h-full flex items-center px-4 sm:px-5 border-r border-axe-border">
          <span className="text-axe-accent font-bold tracking-[0.15em] text-xs uppercase">AXE CAPITAL</span>
        </div>
        <div className="flex flex-1 items-center justify-between px-5 min-w-0 gap-4">
          <span className="text-axe-dim text-xs shrink-0">{TAB_LABELS[activeTab]}</span>
          <FreshnessHeader health={health} />
          <span className="ui-badge text-axe-dim shrink-0">manual execution · IBKR read-only</span>
        </div>
      </header>

      {/* ── Body: sidebar + main ── */}
      <div className="flex flex-col lg:flex-row flex-1 overflow-hidden">
        <AppSidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          navBadges={navBadges}
          refreshToken={refreshToken}
          onRefreshComplete={handleRefreshComplete}
        />

        <main className="flex-1 overflow-y-auto p-3 sm:p-5 min-w-0">
          {/* ── Overview: Daily Brief ── */}
          {activeTab === 'overview' && (
            <div className="space-y-5">
              {commandCenterError ? (
                <div className="panel-card text-sm text-red-300">
                  Failed to load command center: {commandCenterError}
                </div>
              ) : (
                <CommandCenter payload={commandCenter} />
              )}
            </div>
          )}

          {/* ── Portfolio: Watchlist + Targets ── */}
          {activeTab === 'portfolio' && (
            <div className="space-y-5">
              <TargetsPanel key={`targets-${refreshToken}`} />
            </div>
          )}

          {/* ── Research: Alpha + Analysts + Archive ── */}
          {activeTab === 'research' && (
            <div className="space-y-5">
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
                <AlphaPanel key={`alpha-${refreshToken}`} />
                <AnalystReportsPanel key={`analyst-${refreshToken}`} refreshToken={refreshToken} />
              </div>
              <DecisionArchivePanel
                key={`archive-${refreshToken}`}
                onOpenTrace={(id) => {
                  setActiveRunId(id)
                  setActiveTab('ops')
                }}
              />
            </div>
          )}

          {/* ── Committee Room ── */}
          {activeTab === 'committee' && (
            <CommitteePanel key={`committee-${refreshToken}`} refreshToken={refreshToken} />
          )}

          {/* ── Operations: Queue + Weekly Review + Agent Status + Trace ── */}
          {activeTab === 'ops' && (
            <div className="space-y-5">
              <ApprovalQueuePanel key={`queue-${refreshToken}`} refreshToken={refreshToken} />
              <WeeklyReviewPanel key={`weekly-${refreshToken}`} refreshToken={refreshToken} />
              <div className="grid grid-cols-1 xl:grid-cols-5 gap-5">
                <div className="xl:col-span-2">
                  <AgentStatusPanel
                    key={`status-${refreshToken}`}
                    onOpenTrace={setActiveRunId}
                  />
                </div>
                <div className="xl:col-span-3">
                  <TraceViewerPanel
                    key={`trace-${refreshToken}-${activeRunId || 'none'}`}
                    runId={activeRunId}
                  />
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
