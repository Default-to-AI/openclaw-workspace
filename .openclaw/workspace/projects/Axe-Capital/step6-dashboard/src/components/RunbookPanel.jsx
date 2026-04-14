function Badge({ label, className = '' }) {
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-full border border-axe-border bg-axe-muted/20 text-axe-dim ${className}`}>
      {label}
    </span>
  )
}

function LinkRow({ label, href, note }) {
  return (
    <div className="flex items-start justify-between gap-4 py-3 border-b border-axe-border/40 last:border-b-0">
      <div>
        <div className="text-axe-text text-sm font-medium">{label}</div>
        {note && <div className="text-axe-dim text-xs mt-0.5">{note}</div>}
      </div>
      <a
        className="text-axe-accent text-xs underline underline-offset-4"
        href={href}
        target="_blank"
        rel="noreferrer"
      >
        open
      </a>
    </div>
  )
}

export default function RunbookPanel() {
  const items = [
    {
      label: 'Spec: Vision & Non-Negotiables',
      href: 'https://docs.local/axe/spec/00-vision-and-non-negotiables',
      note: 'Human approval gates, paper-first, audit trail'
    },
    {
      label: 'Spec: System Architecture',
      href: 'https://docs.local/axe/spec/02-system-architecture',
      note: 'Orchestrator, research, risk, execution, audit'
    },
    {
      label: 'Runbook: Weekly cycle',
      href: 'https://docs.local/axe/plans/weekly-cycle',
      note: 'Cadence and meetings'
    }
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-axe-text font-semibold text-base tracking-wide">
            Panel 7 — Runbook
          </h2>
          <p className="text-axe-dim text-xs mt-0.5">
            Quick links to specs and operating cadence (placeholder links for now)
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <Badge label={`${items.length} links`} />
        </div>
      </div>

      <div className="bg-axe-surface border border-axe-border rounded-lg p-4">
        {items.map((i) => (
          <LinkRow key={i.label} label={i.label} href={i.href} note={i.note} />
        ))}
      </div>

      <div className="text-axe-dim text-xs">
        Next step: replace placeholders with real local file links once we decide deployment (static site vs served markdown).
      </div>
    </div>
  )
}

