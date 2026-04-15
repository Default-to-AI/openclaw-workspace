import './index.css'
import PortfolioPanel from './components/PortfolioPanel'
import TargetsPanel from './components/TargetsPanel'
import AlphaPanel from './components/AlphaPanel'
import ResearchPanel from './components/ResearchPanel'
import DecisionLogPanel from './components/DecisionLogPanel'
import AutomationPanel from './components/AutomationPanel'
import RunbookPanel from './components/RunbookPanel'

function App() {
  return (
    <div className="min-h-screen bg-axe-bg">
      {/* Top bar */}
      <header className="border-b border-axe-border bg-axe-surface/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-screen-2xl mx-auto px-6 h-12 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-axe-accent font-bold tracking-widest text-sm uppercase">
              AXE CAPITAL
            </span>
            <span className="text-axe-border">|</span>
            <span className="text-axe-dim text-xs">Operations Dashboard</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-axe-dim">
            <span className="flex items-center gap-1.5 text-axe-dim">
              Static · refresh manually
            </span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-screen-2xl mx-auto px-6 py-6">
        <PortfolioPanel />
        <div className="mt-6">
          <TargetsPanel />
        </div>
        <div className="mt-6">
          <AlphaPanel />
        </div>
        <div className="mt-6">
          <ResearchPanel />
        </div>
        <div className="mt-6">
          <DecisionLogPanel />
        </div>
        <div className="mt-6">
          <AutomationPanel />
        </div>
        <div className="mt-6">
          <RunbookPanel />
        </div>
      </main>
    </div>
  )
}

export default App
