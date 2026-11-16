import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi, afterEach } from 'vitest'
import RunDetailPage from '../pages/RunDetailPage'

// Minimal EventSource mock so the page's SSE wiring can be driven in jsdom.
class MockEventSource {
  static instances: MockEventSource[] = []
  listeners: Record<string, (e: MessageEvent) => void> = {}
  closed = false
  constructor(public url: string) {
    MockEventSource.instances.push(this)
  }
  addEventListener(kind: string, cb: (e: MessageEvent) => void) {
    this.listeners[kind] = cb
  }
  close() {
    this.closed = true
  }
  emit(kind: string, seq: number, payload: unknown) {
    const cb = this.listeners[kind]
    if (cb) {
      cb({ lastEventId: String(seq), data: JSON.stringify(payload) } as MessageEvent)
    }
  }
  onerror: (() => void) | null = null
}

const runSucceeded = {
  run_id: 'r1',
  phase: 'P0',
  status: 'succeeded',
  blocked: false,
  blocking_reasons: [],
  split_hash: 'a'.repeat(64),
  config_hash: 'b'.repeat(64),
}

const p0FailGates = [
  { gate_id: 'G-P0-1', status: 'fail', message: 'Codebook usage collapsed to 0.005.' },
  { gate_id: 'G-P0-2', status: 'pass', message: 'grads finite' },
  { gate_id: 'G-P0-3', status: 'pass', message: 'memory ok' },
  { gate_id: 'G-P0-4', status: 'pass', message: 'timing ok' },
]

const p0PassGates = p0FailGates.map((g) => ({ ...g, status: 'pass', message: 'ok' }))

function installFetch() {
  return vi.spyOn(global, 'fetch').mockImplementation((input: RequestInfo | URL) => {
    const url = String(input)
    if (url.includes('/artifacts')) {
      return Promise.resolve(new Response(JSON.stringify({ artifacts: [] }), { status: 200 }))
    }
    return Promise.resolve(new Response(JSON.stringify(runSucceeded), { status: 200 }))
  })
}

afterEach(() => {
  vi.restoreAllMocks()
  MockEventSource.instances = []
})

describe('RunDetailPage gate-driven P1 controls', () => {
  it('marks a failed P0 gate and hides P1 launch controls', async () => {
    installFetch()
    vi.stubGlobal('EventSource', MockEventSource as unknown as typeof EventSource)

    render(<RunDetailPage runId="r1" />)
    await waitFor(() => expect(MockEventSource.instances.length).toBe(1))
    const es = MockEventSource.instances[0]
    es.emit('p0_verdict', 9, {
      gate_id: 'G-P0', status: 'fail',
      message: 'P0 gate failed at: G-P0-1',
      evidence: { gates: p0FailGates },
    })

    await waitFor(() => expect(screen.getAllByText(/G-P0-1/).length).toBeGreaterThan(0))
    const failedGate = screen
      .getByText('Codebook usage collapsed to 0.005.')
      .closest('.gate')
    expect(failedGate).toHaveAttribute('data-status', 'fail')

    expect(screen.queryByTestId('launch-p1')).toBeNull()
    expect(screen.getByTestId('p1-blocked-note')).toBeInTheDocument()
  })

  it('shows the P1 control when all G-P0 gates passed', async () => {
    installFetch()
    vi.stubGlobal('EventSource', MockEventSource as unknown as typeof EventSource)

    render(<RunDetailPage runId="r1" />)
    await waitFor(() => expect(MockEventSource.instances.length).toBe(1))
    MockEventSource.instances[0].emit('p0_verdict', 9, {
      gate_id: 'G-P0', status: 'pass',
      message: 'All G-P0 gates passed.',
      evidence: { gates: p0PassGates },
    })

    await waitFor(() => expect(screen.getByTestId('launch-p1')).toBeInTheDocument())
    expect(screen.queryByTestId('p1-blocked-note')).toBeNull()
  })
})
