import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import CommandCenter from './CommandCenter'

const payload = {
  generated_at: '2026-04-21T00:25:19Z',
  partial: false,
  data_freshness: {},
  decision_inbox: [
    {
      run_id: 'GOOG-1be743bb',
      symbol: 'GOOG',
      action: 'ADD',
      confidence: 8,
      summary: 'Thesis intact, add on dip',
      timestamp: '2026-04-21T00:15:27Z',
    },
  ],
  live_missions: [
    {
      run_id: 'GOOG-1be743bb',
      status: 'running',
      headline: 'committee run in progress',
      latest_summary: 'debate underway',
      updated_at: '2026-04-21T00:12:00Z',
    },
  ],
  watchers: [{ key: 'news', label: 'News Watcher', status: 'stale', partial: false }],
  surveillance_alerts: [{ symbol: 'TSLA', severity: 'RED', thesis: 'Speculative hold.' }],
  firm_exceptions: [{ key: 'news', status: 'stale', age_min: 5885 }],
  current_focus: {
    run_id: 'GOOG-1be743bb',
    status: 'running',
    headline: 'committee run in progress',
    latest_summary: 'debate underway',
    updated_at: '2026-04-21T00:12:00Z',
  },
}

describe('CommandCenter', () => {
  it('shows loading state when payload is null', () => {
    render(<CommandCenter payload={null} />)
    expect(screen.getByText(/loading command center/i)).toBeInTheDocument()
  })

  it('renders the operator-first shell with inbox and mission board', () => {
    render(<CommandCenter payload={payload} />)

    expect(screen.getByRole('heading', { name: 'Command Center' })).toBeInTheDocument()
    expect(screen.getByText('Decision Inbox')).toBeInTheDocument()
    expect(screen.getByText('Live Mission Board')).toBeInTheDocument()
    expect(screen.getByText('GOOG')).toBeInTheDocument()
    expect(screen.getByText('ADD')).toBeInTheDocument()
  })

  it('opens mission takeover mode when a mission row is selected', () => {
    render(<CommandCenter payload={payload} />)

    fireEvent.click(screen.getAllByRole('button', { name: /open mission goog-1be743bb/i })[0])

    expect(screen.getAllByText('Mission Takeover').length).toBeGreaterThan(0)
    expect(screen.getAllByText('debate underway').length).toBeGreaterThan(0)
  })
})
