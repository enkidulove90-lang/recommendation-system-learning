// Typed client for the ADA backend REST/SSE contracts. No direct filesystem
// or GPU calls: everything goes through the backend API.

export type GateStatus = 'pass' | 'fail' | 'warn' | 'blocked'

export interface GateOutcome {
  gate_id: string
  status: GateStatus
  message: string
  evidence?: Record<string, unknown>
}

export interface RunRecord {
  run_id: string
  phase: string
  status: string
  blocked: boolean
  blocking_reasons: string[]
  config_hash?: string | null
  split_hash?: string | null
  pid?: number | null
  return_code?: number | null
  is_synthetic_demo: boolean
}

export interface ValidationOut {
  run_id: string
  blocked: boolean
  reasons: string[]
  human_readable: string
  config_hash?: string | null
  split_hash?: string | null
}

export interface Artifact {
  name: string
  path: string
  sha256?: string | null
  kind: string
}

export interface MetricSeries {
  loss?: (number | null)[]
  codebook_usage?: (number | null)[]
  grad_norm?: (number | null)[]
  memory_mb?: (number | null)[]
  step_ms?: (number | null)[]
  valid_metric?: (number | null)[]
}

export interface SSEEvent {
  seq: number
  event: string
  payload: Record<string, unknown>
}

const BASE = ''

async function handle<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    let detail = resp.statusText
    try {
      const body = await resp.json()
      detail = body.detail ?? JSON.stringify(body)
    } catch {
      /* keep statusText */
    }
    throw new Error(detail)
  }
  return resp.json() as Promise<T>
}

export const api = {
  validateConfig: (body: unknown): Promise<ValidationOut> =>
    fetch(`${BASE}/api/configs/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then((r) => handle<ValidationOut>(r)),

  createRun: (body: unknown): Promise<{ run: RunRecord; validation: ValidationOut }> =>
    fetch(`${BASE}/api/runs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then((r) => handle<{ run: RunRecord; validation: ValidationOut }>(r)),

  listRuns: (): Promise<{ runs: RunRecord[] }> =>
    fetch(`${BASE}/api/runs`).then((r) => handle<{ runs: RunRecord[] }>(r)),

  runDetail: (runId: string): Promise<RunRecord> =>
    fetch(`${BASE}/api/runs/${runId}`).then((r) => handle<RunRecord>(r)),

  startRun: (runId: string): Promise<RunRecord> =>
    fetch(`${BASE}/api/runs/${runId}/start`, { method: 'POST' }).then((r) => handle<RunRecord>(r)),

  cancelRun: (runId: string): Promise<RunRecord> =>
    fetch(`${BASE}/api/runs/${runId}/cancel`, { method: 'POST' }).then((r) => handle<RunRecord>(r)),

  artifacts: (runId: string): Promise<{ artifacts: Artifact[] }> =>
    fetch(`${BASE}/api/runs/${runId}/artifacts`).then(
      (r) => handle<{ artifacts: Artifact[] }>(r),
    ),
}

// SSE with Last-Event-ID resume support.
export function openEventStream(
  runId: string,
  lastSeq: number,
  onEvent: (ev: SSEEvent) => void,
  onClose: () => void,
): () => void {
  const es = new EventSource(`${BASE}/api/runs/${runId}/events?last_seq=${lastSeq}`)
  const kinds = ['run_created', 'run_started', 'step_metrics', 'eval_metrics', 'p0_verdict', 'config_blocked', 'run_terminal']
  kinds.forEach((kind) => {
    es.addEventListener(kind, (e) => {
      const me = e as MessageEvent
      onEvent({
        seq: Number(me.lastEventId),
        event: kind,
        payload: JSON.parse(me.data),
      })
      if (kind === 'run_terminal' || kind === 'config_blocked') {
        es.close()
        onClose()
      }
    })
  })
  es.onerror = () => {
    // Browser retry semantics keep resume-from-id behavior.
  }
  return () => es.close()
}
