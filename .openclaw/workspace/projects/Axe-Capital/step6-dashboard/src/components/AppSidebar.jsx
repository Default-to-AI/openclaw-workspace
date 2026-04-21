import { useEffect, useState } from 'react'
import { fetchHealthStatus, triggerRefresh } from '../lib/api'

const REFRESH_TARGETS = [
  { id: 'all', label: 'Run all', primary: true },
  { id: 'portfolio', label: 'Portfolio', primary: false },
  { id: 'specialists_decide', label: 'Specialists + Decision', primary: false },
  { id: 'alpha', label: 'Alpha', primary: false },
  { id: 'news', label: 'News', primary: false },
]

const NAV_ITEMS = [
  {
    id: 'overview',
    label: 'Overview',
    icon: (
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4 flex-shrink-0">
        <circle cx="8" cy="8" r="6" /><circle cx="8" cy="8" r="2.5" />
      </svg>
    ),
  },
  {
    id: 'portfolio',
    label: 'Portfolio',
    icon: (
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4 flex-shrink-0">
        <rect x="1" y="9" width="3" height="6" rx="1" /><rect x="6" y="5" width="3" height="10" rx="1" /><rect x="11" y="1" width="3" height="14" rx="1" />
      </svg>
    ),
  },
  {
    id: 'research',
    label: 'Research',
    icon: (
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4 flex-shrink-0">
        <circle cx="6.5" cy="6.5" r="4" /><line x1="10" y1="10" x2="14" y2="14" />
      </svg>
    ),
  },
  {
    id: 'ops',
    label: 'Operations',
    icon: (
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4 flex-shrink-0">
        <path d="M8 2v3M8 11v3M2 8h3M11 8h3" /><circle cx="8" cy="8" r="2.5" />
      </svg>
    ),
  },
  {
    id: 'committee',
    label: 'Committee',
    icon: (
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4 flex-shrink-0">
        <circle cx="4" cy="5" r="2" /><circle cx="12" cy="5" r="2" /><circle cx="8" cy="11" r="2" />
        <line x1="4" y1="7" x2="8" y2="9" /><line x1="12" y1="7" x2="8" y2="9" />
      </svg>
    ),
  },
]

function NavBadge({ badge }) {
  if (!badge) return null
  return (
    <span className={`ml-auto inline-flex items-center rounded-full border px-1.5 py-0.5 text-[10px] leading-none ${badge.tone}`}>
      {badge.label}
    </span>
  )
}

function FreshnessRow({ label, artifact }) {
  if (!artifact) return null
  const tone =
    artifact.status === 'fresh'
      ? 'text-emerald-300 border-emerald-700/60 bg-emerald-900/10'
      : artifact.status === 'stale'
        ? 'text-amber-300 border-amber-700/60 bg-amber-900/10'
        : 'text-red-300 border-red-700/60 bg-red-900/10'
  const age = artifact.age_min != null ? `${artifact.age_min}m` : artifact.status
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className="text-axe-dim text-[11px]">{label}</span>
      <span className={`inline-flex items-center rounded-full border px-1.5 py-0.5 text-[10px] leading-none ${tone}`}>{age}</span>
    </div>
  )
}

export default function AppSidebar({ activeTab, onTabChange, navBadges = {}, refreshToken, onRefreshComplete }) {
  const [health, setHealth] = useState(null)
  const [runningTarget, setRunningTarget] = useState(null)
  const [refreshError, setRefreshError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchHealthStatus()
      .then(({ data }) => { if (!cancelled) setHealth(data) })
      .catch(() => {})
    return () => { cancelled = true }
  }, [refreshToken])

  async function handleRefresh(target) {
    setRunningTarget(target)
    setRefreshError(null)
    try {
      const result = await triggerRefresh(target)
      onRefreshComplete?.(result)
    } catch (err) {
      setRefreshError(err.message)
    } finally {
      setRunningTarget(null)
    }
  }

  const artifacts = health?.artifacts || {}

  return (
    <nav className="w-[210px] flex-shrink-0 flex flex-col border-r border-axe-border bg-axe-surface overflow-y-auto">
      {/* Navigation */}
      <div className="px-3 pt-4 pb-1">
        <div className="text-axe-muted text-[10px] uppercase tracking-wider px-2 mb-1">Navigate</div>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={[
              'w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-xs text-left transition-all duration-100',
              'border-l-2',
              activeTab === item.id
                ? 'border-axe-accent text-[#a5b4fc] bg-axe-accent/10'
                : 'border-transparent text-axe-dim hover:text-axe-text hover:bg-white/[0.03]',
            ].join(' ')}
          >
            <span className={activeTab === item.id ? 'opacity-100' : 'opacity-70'}>{item.icon}</span>
            <span>{item.label}</span>
            <NavBadge badge={navBadges[item.id]} />
          </button>
        ))}
      </div>

      {/* Refresh */}
      <div className="px-3 py-3 border-t border-axe-border mt-2">
        <div className="text-axe-muted text-[10px] uppercase tracking-wider px-2 mb-2">Refresh</div>
        <div className="space-y-1">
          {REFRESH_TARGETS.map((t) => {
            const busy = runningTarget === t.id || (t.id === 'all' && runningTarget !== null)
            return (
              <button
                key={t.id}
                onClick={() => handleRefresh(t.id)}
                disabled={runningTarget !== null}
                className={[
                  'w-full text-[11px] font-medium px-3 py-1.5 rounded-md transition-all text-left',
                  t.primary
                    ? 'bg-axe-accent text-white hover:opacity-90 disabled:opacity-50 text-center'
                    : 'border border-axe-border text-axe-text hover:bg-white/[0.04] disabled:opacity-50',
                ].join(' ')}
              >
                {busy ? `Running…` : t.label}
              </button>
            )
          })}
        </div>
        {refreshError && (
          <div className="mt-2 text-[10px] text-red-300 px-2">Error: {refreshError}</div>
        )}
      </div>

      {/* Freshness — pinned to bottom */}
      <div className="mt-auto px-3 py-3 border-t border-axe-border">
        <div className="text-axe-muted text-[10px] uppercase tracking-wider px-2 mb-2">Data Freshness</div>
        <div className="space-y-0.5 px-1">
          <FreshnessRow label="portfolio" artifact={artifacts.portfolio} />
          <FreshnessRow label="alpha" artifact={artifacts.alpha} />
          <FreshnessRow label="news" artifact={artifacts.news} />
          <FreshnessRow label="decision" artifact={artifacts.decision} />
          <FreshnessRow label="analysts" artifact={artifacts.analyst_reports} />
        </div>
      </div>
    </nav>
  )
}
