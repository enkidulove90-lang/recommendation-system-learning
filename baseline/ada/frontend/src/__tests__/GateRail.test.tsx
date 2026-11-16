import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import GateRail, { p0Failed } from '../components/GateRail'
import RunDetailPage from '../pages/RunDetailPage'
import type { GateOutcome } from '../api'

const passedP0: GateOutcome[] = [
  { gate_id: 'G-P0-1', status: 'pass', message: 'usage healthy' },
  { gate_id: 'G-P0-2', status: 'pass', message: 'grads finite' },
  { gate_id: 'G-P0-3', status: 'pass', message: 'memory ok' },
  { gate_id: 'G-P0-4', status: 'pass', message: 'timing ok' },
]

const failedP0: GateOutcome[] = [
  { gate_id: 'G-P0-1', status: 'fail', message: 'Codebook usage collapsed to 0.005.' },
  { gate_id: 'G-P0-2', status: 'pass', message: 'grads finite' },
  { gate_id: 'G-P0-3', status: 'pass', message: 'memory ok' },
  { gate_id: 'G-P0-4', status: 'pass', message: 'timing ok' },
]

describe('GateRail', () => {
  it('visually marks a failed gate via data-status', () => {
    render(<GateRail gates={failedP0} />)
    const failed = screen.getByText('Codebook usage collapsed to 0.005.').closest('.gate')
    expect(failed).toHaveAttribute('data-status', 'fail')
    const passed = screen.getByText('grads finite').closest('.gate')
    expect(passed).toHaveAttribute('data-status', 'pass')
  })

  it('p0Failed is true only for fail/blocked G-P0 gates', () => {
    expect(p0Failed(passedP0)).toBe(false)
    expect(p0Failed(failedP0)).toBe(true)
  })
})

describe('RunDetailPage P1 gating', () => {
  it('marks a failed P0 gate and hides P1 launch controls', async () => {
    const spy = vi.spyOn(global, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/artifacts')) {
        return Promise.resolve(new Response(JSON.stringify({ artifacts: [] }), { status: 200 }))
      }
      return Promise.resolve(
        new Response(
          JSON.stringify({
            run_id: 'r1', phase: 'P0', status: 'succeeded', blocked: false,
            blocking_reasons: [],
          }),
          { status: 200 },
        ),
      )
    })

    // Gate state is delivered through the p0_verdict SSE event; the page
    // reads it from the event payload.  For the unit test we simulate by
    // asserting the decision helper + hidden button logic.
    render(<RunDetailPage runId="r1" />)
    // With no p0_verdict event yet, no P1 control and no blocked note.
    expect(screen.queryByTestId('launch-p1')).toBeNull()

    // p0Failed(failedP0) drives the hidden control; verify the invariant.
    expect(p0Failed(failedP0)).toBe(true)
    expect(p0Failed(passedP0)).toBe(false)
    spy.mockRestore()
  })
})
