import './index.css'
import PortfolioPanel from './components/PortfolioPanel'

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
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-axe-green inline-block animate-pulse" />
              LIVE
            </span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-screen-2xl mx-auto px-6 py-6">
        <PortfolioPanel />
      </main>
    </div>
  )
}

export default App
