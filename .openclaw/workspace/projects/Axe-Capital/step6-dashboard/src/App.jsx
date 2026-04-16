import { useState } from 'react'
import './index.css'
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
import RefreshBar from './components/RefreshBar'

function App() {
  const [activeRunId, setActiveRunId] = useState(null)
  const [refreshToken, setRefreshToken] = useState(0)

  function handleRefreshComplete() {
    setRefreshToken((value) => value + 1)
  }

  return (
    <div className="min-h-screen bg-axe-bg">
      <header className="border-b border-axe-border bg-axe-surface/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-screen-2xl mx-auto px-6 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-axe-accent font-bold tracking-widest text-sm uppercase">
              AXE CAPITAL
            </span>
            <span className="text-axe-border">|</span>
            <span className="text-axe-dim text-xs truncate">Research Platform</span>
          </div>
          <div className="hidden md:flex items-center gap-2 text-xs">
            <span className="ui-badge text-emerald-300 border-emerald-700/60 bg-emerald-900/10">manual execution</span>
            <span className="ui-badge text-axe-dim">IBKR remains broker of record</span>
          </div>
        </div>
      </header>

      <main className="max-w-screen-2xl mx-auto px-6 py-6 space-y-6">
        <RefreshBar onRefreshComplete={handleRefreshComplete} />

        <PortfolioPanel key={`portfolio-${refreshToken}`} />
        <TargetsPanel key={`targets-${refreshToken}`} />

        <div className="grid grid-cols-1 2xl:grid-cols-2 gap-6">
          <AlphaPanel key={`alpha-${refreshToken}`} />
          <NewsPanel key={`news-${refreshToken}`} />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
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

        <DecisionReportPanel key={`decision-report-${refreshToken}`} refreshToken={refreshToken} />
        <AnalystReportsPanel key={`analyst-${refreshToken}`} refreshToken={refreshToken} />
        <WeeklyReviewPanel key={`weekly-${refreshToken}`} refreshToken={refreshToken} />

        <DecisionArchivePanel
          key={`archive-${refreshToken}`}
          onOpenTrace={setActiveRunId}
        />
      </main>
    </div>
  )
}

export default App
