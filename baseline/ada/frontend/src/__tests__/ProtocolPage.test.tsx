import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import ProtocolPage, { defaultParamRows, toRequestBody, type ProtocolForm } from '../pages/ProtocolPage'
import type { ValidationOut } from '../api'

const ALL_PARAMS = [
  'r3vae_L', 'r3vae_M', 'r3vae_top_k', 'mmq_expert_hidden', 'fusion_dim',
  'downstream_hidden', 'neg_pool_size', 'neg_per_positive', 'eval_topk',
  'grad_clip_norm', 'weight_decay', 'warmup_steps',
]

const blockedValidation: ValidationOut = {
  run_id: 'r1',
  blocked: true,
  reasons: [
    "Appendix-A parameter 'r3vae_L' is unresolved (value=None, resolved=False); resolve it with an explicit rationale before launching a run.",
    "Appendix-A parameter 'r3vae_M' is unresolved (value=None, resolved=False); resolve it with an explicit rationale before launching a run.",
  ],
  human_readable: 'Blocked: Appendix-A parameter r3vae_L is unresolved.',
}

const okValidation: ValidationOut = {
  run_id: 'r1',
  blocked: false,
  reasons: [],
  human_readable: 'Protocol checks passed; run may be launched.',
}

describe('ProtocolPage blocked-state gating', () => {
  it('renders 12 unresolved parameters and keeps Start disabled before validation', () => {
    render(<ProtocolPage onCreated={() => {}} />)

    for (const name of ['r3vae_L', 'neg_pool_size', 'warmup_steps']) {
      expect(screen.getByText(name)).toBeInTheDocument()
    }
    expect(screen.getByText(/12\/12 unresolved/)).toBeInTheDocument()

    const start = screen.getByTestId('start-run') as HTMLButtonElement
    expect(start).toBeDisabled()
    // No blocked banner before any validation round-trip.
    expect(screen.queryByTestId('blocked-banner')).toBeNull()
  })

  it('shows the blocked banner with human-readable reasons after a blocked validation', async () => {
    const user = userEvent.setup()
    const spy = vi
      .spyOn(global, 'fetch')
      .mockImplementation(() =>
        Promise.resolve(new Response(JSON.stringify(blockedValidation), { status: 200 })),
      )

    render(<ProtocolPage onCreated={() => {}} />)
    await user.click(screen.getByText('Validate'))

    const banner = screen.getByTestId('blocked-banner')
    expect(banner).toHaveTextContent('Blocked')
    expect(banner).toHaveTextContent('r3vae_L')
    expect((screen.getByTestId('start-run') as HTMLButtonElement).disabled).toBe(true)
    spy.mockRestore()
  })

  it('enables Start only after all parameters are resolved and validation passes', async () => {
    const user = userEvent.setup()
    const spy = vi.spyOn(global, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/api/configs/validate')) {
        return Promise.resolve(new Response(JSON.stringify(okValidation), { status: 200 }))
      }
      if (url.endsWith('/start')) {
        return Promise.resolve(
          new Response(JSON.stringify({ run_id: 'r1', status: 'running' }), { status: 200 }),
        )
      }
      return Promise.resolve(
        new Response(JSON.stringify({ run: { run_id: 'r1' }, validation: okValidation }), { status: 200 }),
      )
    })

    render(<ProtocolPage onCreated={() => {}} />)

    for (const name of ALL_PARAMS) {
      await user.type(screen.getByLabelText(`value-${name}`), '2')
      await user.type(screen.getByLabelText(`rationale-${name}`), 'pilot rationale')
    }
    await user.type(screen.getByLabelText('run id'), 'r1')

    expect(screen.getByText(/0\/12 unresolved/)).toBeInTheDocument()
    await user.click(screen.getByText('Validate'))
    expect((screen.getByTestId('start-run') as HTMLButtonElement).disabled).toBe(false)

    spy.mockRestore()
  })
})

describe('request body contract', () => {
  it('marks unresolved params and never claims resolution', () => {
    const form: ProtocolForm = {
      runId: 'r1', phase: 'P0', datasetName: 'd', trainDir: 'x', featurePath: '', seed: 42,
    }
    const body = toRequestBody(form, defaultParamRows()) as {
      appendix_params: { resolved: boolean; value: number | null }[]
    }
    expect(body.appendix_params).toHaveLength(12)
    expect(body.appendix_params.every((p) => !p.resolved && p.value === null)).toBe(true)
  })
})
