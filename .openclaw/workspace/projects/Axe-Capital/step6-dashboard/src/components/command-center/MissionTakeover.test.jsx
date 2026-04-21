import React from 'react'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

afterEach(cleanup)

import MissionTakeover from './MissionTakeover'

describe('MissionTakeover', () => {
  it('shows disconnect state when the mission stream drops', () => {
    render(
      <MissionTakeover
        mission={{ run_id: 'GOOG-1be743bb', stream_error: 'Committee stream disconnected' }}
      />,
    )
    expect(screen.getByText('Committee stream disconnected')).toBeInTheDocument()
  })

  it('renders mission run id and latest summary', () => {
    render(
      <MissionTakeover
        mission={{
          run_id: 'GOOG-1be743bb',
          status: 'running',
          latest_summary: 'risk review complete',
          updated_at: '2026-04-21T00:13:00Z',
        }}
      />,
    )
    expect(screen.getByText('GOOG-1be743bb')).toBeInTheDocument()
    expect(screen.getAllByText('risk review complete').length).toBeGreaterThan(0)
  })

  it('renders nothing when no mission is selected', () => {
    const { container } = render(<MissionTakeover mission={null} />)
    expect(container.firstChild).toBeNull()
  })
})
