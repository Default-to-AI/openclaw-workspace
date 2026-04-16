import { useEffect, useState } from 'react'
import { fetchJsonWithFallback } from '../lib/api'

const AGENT_LABELS = {
  fundamental: 'Fundamental',
  technical: 'Technical',
  macro: 'Macro',
}

function ReportView({ report }) {
  if (!report) return <div className="text-axe-dim text-xs">No report loaded.</div>

  const findings = report.key_findings || {}

  return (
    <div className="space-y-4">
      {report.summary && (
        <p className="text-sm text-axe-text leading-6">{report.summary}</p>
      )}

      {report.confidence && (
        <div className="flex items-center gap-2">
          <span className="text-axe-dim text-xs uppercase tracking-wider">Confidence</span>
          <span className="ui-badge text-axe-dim border-axe-border bg-axe-muted/20">{report.confidence}</span>
        </div>
      )}

      {Object.keys(findings).length > 0 && (
        <div>
          <div className="text-axe-dim text-xs uppercase tracking-wider mb-2">Key Findings</div>
          <div className="space-y-2">
            {Object.entries(findings).map(([k, v]) => (
              <div key={k} className="text-xs">
                <span className="text-axe-dim">{k}: </span>
                <span className="text-axe-text">
                  {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {report.report && (
        <div>
          <div className="text-axe-dim text-xs uppercase tracking-wider mb-2">Full Report</div>
          <p className="text-xs text-axe-dim leading-5 whitespace-pre-wrap">{report.report}</p>
        </div>
      )}

      {report.data_sources?.length > 0 && (
        <div className="text-axe-dim text-xs">
          Sources: {report.data_sources.join(', ')}
        </div>
      )}
    </div>
  )
}

export default function AnalystReportsPanel({ refreshToken }) {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState(null)
  const [selectedSymbol, setSelectedSymbol] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState('fundamental')
  const [report, setReport] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [reportError, setReportError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setIndex(null)
    setError(null)
    fetchJsonWithFallback({ filePath: '/analyst-reports/index.json' })
      .then((payload) => {
        if (cancelled) return
        setIndex(payload)
        const symbols = Object.keys(payload.symbols || {})
        if (symbols.length > 0) setSelectedSymbol(symbols[0])
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
      })
    return () => { cancelled = true }
  }, [refreshToken])

  useEffect(() => {
    if (!index || !selectedSymbol) return
    const meta = index.symbols?.[selectedSymbol]?.[selectedAgent]
    if (!meta?.json_path) { setReport(null); return }

    let cancelled = false
    setReportLoading(true)
    setReportError(null)
    setReport(null)
    fetchJsonWithFallback({ filePath: `/analyst-reports/${meta.json_path}` })
      .then((payload) => {
        if (cancelled) return
        setReport(payload)
        setReportLoading(false)
      })
      .catch((err) => {
        if (cancelled) return
        setReportError(err.message)
        setReportLoading(false)
      })
    return () => { cancelled = true }
  }, [index, selectedSymbol, selectedAgent])

  const symbols = Object.keys(index?.symbols || {})

  return (
    <section className="panel-card">
      <div className="panel-header">
        <div>
          <div className="panel-title">Analyst Reports</div>
          <p className="text-axe-dim text-xs mt-1">
            Per-ticker fundamental · technical · macro from specialist agents
          </p>
        </div>
        <div className="text-axe-dim text-xs">
          {index ? `${symbols.length} symbol${symbols.length !== 1 ? 's' : ''} · ${index.generated_at || ''}` : 'loading…'}
        </div>
      </div>

      {error && <div className="mt-4 text-sm text-red-300">Failed to load analyst index: {error}</div>}

      {!error && index && (
        <div className="mt-4 space-y-4">
          {/* Controls */}
          <div className="flex flex-wrap gap-2">
            {symbols.map((sym) => (
              <button
                key={sym}
                className={selectedSymbol === sym ? 'ui-button' : 'ui-button-secondary'}
                onClick={() => setSelectedSymbol(sym)}
              >
                {sym}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            {Object.entries(AGENT_LABELS).map(([agent, label]) => {
              const hasMeta = !!index.symbols?.[selectedSymbol]?.[agent]
              return (
                <button
                  key={agent}
                  className={selectedAgent === agent ? 'ui-button' : 'ui-button-secondary'}
                  onClick={() => setSelectedAgent(agent)}
                  disabled={!hasMeta}
                >
                  {label}
                  {!hasMeta && ' (—)'}
                </button>
              )
            })}
          </div>

          {/* Report area */}
          <div className="bg-axe-bg/30 border border-axe-border rounded-lg p-4">
            {reportLoading && <div className="text-sm text-axe-dim">Loading {selectedAgent} report for {selectedSymbol}…</div>}
            {reportError && <div className="text-sm text-red-300">Failed to load report: {reportError}</div>}
            {!reportLoading && !reportError && <ReportView report={report} />}
          </div>
        </div>
      )}

      {!error && !index && (
        <div className="mt-4 text-sm text-axe-dim">Loading analyst index…</div>
      )}
    </section>
  )
}
