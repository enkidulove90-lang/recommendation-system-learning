import { useMemo, useState } from 'react'
import { api, type ValidationOut } from '../api'

export const APPENDIX_A_PARAMS = [
  'r3vae_L',
  'r3vae_M',
  'r3vae_top_k',
  'mmq_expert_hidden',
  'fusion_dim',
  'downstream_hidden',
  'neg_pool_size',
  'neg_per_positive',
  'eval_topk',
  'grad_clip_norm',
  'weight_decay',
  'warmup_steps',
] as const

export interface ParamRow {
  name: string
  value: number | null
  resolved: boolean
  rationale: string
}

export function defaultParamRows(): ParamRow[] {
  return APPENDIX_A_PARAMS.map((name) => ({
    name,
    value: null,
    resolved: false,
    rationale: '',
  }))
}

export interface ProtocolForm {
  runId: string
  phase: 'P0' | 'P1' | 'P2'
  datasetName: string
  trainDir: string
  featurePath: string
  seed: number
}

/**
 * Protocol configuration page.
 *
 * Start is disabled while the backend reports a blocked configuration; the
 * unresolved Appendix-A parameters are rendered prominently with their
 * human-readable blocking reasons.
 */
export default function ProtocolPage({ onCreated }: { onCreated: (runId: string) => void }) {
  const [form, setForm] = useState<ProtocolForm>({
    runId: '',
    phase: 'P0',
    datasetName: 'mmssl_baby',
    trainDir: '',
    featurePath: '',
    seed: 42,
  })
  const [params, setParams] = useState<ParamRow[]>(defaultParamRows())
  const [validation, setValidation] = useState<ValidationOut | null>(null)
  const [error, setError] = useState<string>('')
  const [busy, setBusy] = useState(false)

  const unresolved = useMemo(() => params.filter((p) => !p.resolved || p.value === null || !p.rationale.trim()), [params])

  const updateParam = (name: string, patch: Partial<ParamRow>) => {
    setParams((rows) => rows.map((r) => (r.name === name ? { ...r, ...patch } : r)))
    setValidation(null)
  }

  const validate = async () => {
    setBusy(true)
    setError('')
    try {
      const body = toRequestBody(form, params)
      const out = await api.validateConfig(body)
      setValidation(out)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  const createAndStart = async () => {
    setBusy(true)
    setError('')
    try {
      const body = toRequestBody(form, params)
      const validation = await api.validateConfig(body)
      setValidation(validation)
      if (validation.blocked) return
      const { run } = await api.createRun(body)
      await api.startRun(run.run_id)
      onCreated(run.run_id)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  const blocked = validation?.blocked ?? unresolved.length > 0

  return (
    <div>
      {validation?.blocked && (
        <div className="blocked-banner" data-testid="blocked-banner">
          <strong>{validation.human_readable}</strong>
          <ul>
            {validation.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="panel" style={{ marginBottom: 14 }}>
        <h2>Protocol Configuration</h2>
        <table className="dense">
          <tbody>
            <tr>
              <td>Run ID</td>
              <td>
                <input
                  aria-label="run id"
                  value={form.runId}
                  onChange={(e) => setForm({ ...form, runId: e.target.value })}
                />
              </td>
            </tr>
            <tr>
              <td>Phase</td>
              <td>
                <select
                  aria-label="phase"
                  value={form.phase}
                  onChange={(e) => setForm({ ...form, phase: e.target.value as 'P0' | 'P1' | 'P2' })}
                >
                  <option>P0</option>
                  <option>P1</option>
                  <option>P2</option>
                </select>
              </td>
            </tr>
            <tr>
              <td>Train dir</td>
              <td>
                <input
                  aria-label="train dir"
                  value={form.trainDir}
                  onChange={(e) => setForm({ ...form, trainDir: e.target.value })}
                  placeholder="baseline/LightGCNpp/data/amazon-baby-mmssl"
                />
              </td>
            </tr>
            <tr>
              <td>Feature path</td>
              <td>
                <input
                  aria-label="feature path"
                  value={form.featurePath}
                  onChange={(e) => setForm({ ...form, featurePath: e.target.value })}
                  placeholder="…/image_feat.npy"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="panel" style={{ marginBottom: 14 }}>
        <h2>Appendix-A Parameters ({unresolved.length}/12 unresolved)</h2>
        <div className="param-grid">
          {params.map((p) => (
            <div key={p.name} className={`param ${p.resolved && p.value !== null && p.rationale.trim() ? 'resolved' : 'unresolved'}`}>
              <div className="p-name">{p.name}</div>
              <div className="p-value">
                {p.resolved && p.value !== null ? `value=${p.value}` : 'unresolved'}
              </div>
              <input
                aria-label={`value-${p.name}`}
                placeholder="value"
                value={p.value === null ? '' : String(p.value)}
                onChange={(e) =>
                  updateParam(p.name, {
                    value: e.target.value === '' ? null : Number(e.target.value),
                    resolved: e.target.value !== '' && p.rationale.trim().length > 0,
                  })
                }
              />
              <input
                aria-label={`rationale-${p.name}`}
                placeholder="rationale (required)"
                value={p.rationale}
                onChange={(e) =>
                  updateParam(p.name, {
                    rationale: e.target.value,
                    resolved: e.target.value.trim().length > 0 && p.value !== null,
                  })
                }
              />
            </div>
          ))}
        </div>
      </div>

      {error && <div className="blocked-banner">{error}</div>}

      <button className="btn" onClick={validate} disabled={busy}>
        Validate
      </button>
      <button
        className="btn"
        style={{ marginLeft: 10 }}
        onClick={createAndStart}
        disabled={busy || blocked || !form.runId}
        data-testid="start-run"
      >
        Start run
      </button>
    </div>
  )
}

export function toRequestBody(form: ProtocolForm, params: ParamRow[]) {
  return {
    run_id: form.runId,
    phase: form.phase,
    dataset_name: form.datasetName,
    seed: form.seed,
    train_dir: form.trainDir,
    feature_paths: form.featurePath ? { image: form.featurePath } : {},
    appendix_params: params.map((p) => ({
      name: p.name,
      value: p.value,
      resolved: p.resolved,
      rationale: p.rationale,
      source: 'console',
    })),
    max_steps: 200,
    eval_interval: 20,
    log_interval: 5,
  }
}
