import { describe, expect, it, vi, afterEach } from 'vitest'

import { loadCommandCenter, mergeMissionEvent } from './store'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('loadCommandCenter', () => {
  it('loads the normalized payload from the API first', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ generated_at: '2026-04-21T00:25:19Z', partial: false }),
      }),
    )

    const payload = await loadCommandCenter(() => 'fixed')

    expect(payload.generated_at).toBe('2026-04-21T00:25:19Z')
    expect(fetch).toHaveBeenCalledWith('/api/command-center?_=fixed', { cache: 'no-store' })
  })

  it('falls back to the static artifact when the API is unavailable', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockRejectedValueOnce(new Error('down'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ generated_at: '2026-04-21T00:25:19Z', partial: true }),
        }),
    )

    const payload = await loadCommandCenter(() => 'fixed')

    expect(payload.partial).toBe(true)
    expect(fetch).toHaveBeenNthCalledWith(1, '/api/command-center?_=fixed', { cache: 'no-store' })
    expect(fetch).toHaveBeenNthCalledWith(2, '/command-center.json?_=fixed', { cache: 'no-store' })
  })
})

describe('mergeMissionEvent', () => {
  it('merges committee stream events into the selected mission', () => {
    const state = {
      live_missions: [
        { run_id: 'GOOG-1be743bb', status: 'running', latest_summary: 'initial', updated_at: '2026-04-21T00:10:00Z' },
      ],
      current_focus: { run_id: 'GOOG-1be743bb', status: 'running', latest_summary: 'initial', updated_at: '2026-04-21T00:10:00Z' },
    }

    const next = mergeMissionEvent(state, {
      run_id: 'GOOG-1be743bb',
      status: 'running',
      latest_summary: 'risk review complete',
      updated_at: '2026-04-21T00:13:00Z',
    })

    expect(next.current_focus.latest_summary).toBe('risk review complete')
    expect(next.live_missions[0].latest_summary).toBe('risk review complete')
  })

  it('keeps the fresher mission update instead of overwriting with stale data', () => {
    const state = {
      live_missions: [
        { run_id: 'GOOG-1be743bb', status: 'running', latest_summary: 'new', updated_at: '2026-04-21T00:12:00Z' },
      ],
      current_focus: { run_id: 'GOOG-1be743bb', status: 'running', latest_summary: 'new', updated_at: '2026-04-21T00:12:00Z' },
    }

    const next = mergeMissionEvent(state, {
      run_id: 'GOOG-1be743bb',
      status: 'running',
      latest_summary: 'old',
      updated_at: '2026-04-21T00:11:00Z',
    })

    expect(next.live_missions[0].latest_summary).toBe('new')
    expect(next.current_focus.latest_summary).toBe('new')
  })
})
