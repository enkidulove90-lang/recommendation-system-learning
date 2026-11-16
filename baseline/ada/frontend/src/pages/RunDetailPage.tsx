import { useEffect, useRef, useState } from 'react'
import {
  api,
  openEventStream,
  type GateOutcome,
  type MetricSeries,
  type RunRecord,
  type SSEEvent,
} from '../api'
import GateRail, { p0Failed } from '../components/GateRail'
import MetricCharts from '../components/MetricCharts'
import DeviationRegister from '../components/DeviationRegister'

interface Props {
  runId: string
}

/**
 * Run detail page: gate rail, live metrics (SSE), artifacts, and the P1
 * launch control.  The P1 control is hidden whenever a G-P0 gate failed —
 * a failed P0 gate can never be followed by a P1 launch from the UI.
 */
export default function RunDetailPage({ runId }: Props) {
  const [run, setRun] = useState<RunRecord | null>(null)
  const [gates, setGates] = useState<GateOutcome[]>([])
  const [metrics, setMetrics] = useState<MetricSeries>({})
  const [events, setEvents] = useState<SSEEvent[]>([])
  const [artifacts, setArtifacts] = useState<{ name: string; kind: string }[]>([])
  const lastSeq = useRef(0)
  const metricsRef = useRef<MetricSeries>({})

  useEffect(() => {
    let closed = false
    let disconnect = () => {}

    const refresh = async () => {
      const detail = await api.runDetail(runId)
      setRun(detail)
    }

    refresh().then(() => {
      if (closed) return
      disconnect = openEventStream(
        runId,
        lastSeq.current,
        (ev) => {
          lastSeq.current = Math.max(lastSeq.current, ev.seq)
          setEvents((prev) => [...prev, ev])
          if (ev.event === 'p0_verdict') {
            const payload = ev.payload as { evidence?: { gates?: GateOutcome[] } }
            const inner = payload.evidence?.gates ?? []
            setGates(inner.length ? inner : [payload as unknown as GateOutcome])
          }
          if (ev.event === 'step_metrics') {
            const p = ev.payload as { step: number; loss?: number; grad_norm?: number; memory_mb?: number; step_ms?: number }
            const push = (key: keyof MetricSeries, value?: number) => {
              if (value === undefined) return
              const arr = [...(metricsRef.current[key] ?? [])]
              // Fill gaps for any step that did not emit this metric.
              while (arr.length < p.step - 1) arr.push(null)
              arr[p.step - 1] = value
              metricsRef.current = { ...metricsRef.current, [key]: arr }
            }
            push('loss', p.loss)
            push('grad_norm', p.grad_norm)
            push('memory_mb', p.memory_mb)
            push('step_ms', p.step_ms)
            setMetrics(metricsRef.current)
          }
          if (ev.event === 'eval_metrics') {
            const p = ev.payload as { step: number; valid_auc?: number }
            const arr = [...(metricsRef.current.valid_metric ?? [])]
            while (arr.length < p.step - 1) arr.push(null)
            arr[p.step - 1] = p.valid_auc ?? null
            metricsRef.current = { ...metricsRef.current, valid_metric: arr }
            setMetrics(metricsRef.current)
          }
        },
        () => {
          api.artifacts(runId).then((a) => setArtifacts(a.artifacts)).catch(() => {})
          refresh()
        },
      )
    })

    return () => {
      closed = true
      disconnect()
    }
  }, [runId])

  const cancel = async () => {
    const updated = await api.cancelRun(runId)
    setRun(updated)
  }

  if (!run) return <div className="panel">loading…</div>

  const p1Blocked = p0Failed(gates)
  const canLaunchP1 = run.phase === 'P0' && run.status === 'succeeded' && !p1Blocked

  return (
    <div>
      <div className="panel" style={{ marginBottom: 14 }}>
        <h2>
          Run {run.run_id} <span className={`status-chip ${run.status}`}>{run.status}</span>
        </h2>
        <table className="dense">
          <tbody>
            <tr><td>Phase</td><td>{run.phase}</td></tr>
            <tr><td>Split hash</td><td>{run.split_hash ?? '—'}</td></tr>
            <tr><td>Config hash</td><td>{run.config_hash ?? '—'}</td></tr>
            <tr><td>Return code</td><td>{run.return_code ?? '—'}</td></tr>
          </tbody>
        </table>
        {run.status === 'running' && (
          <button className="btn danger" style={{ marginTop: 10 }} onClick={cancel}>
            Cancel run
          </button>
        )}
        {canLaunchP1 && (
          <button className="btn" style={{ marginTop: 10, marginLeft: 10 }} data-testid="launch-p1">
            Launch P1
          </button>
        )}
        {p1Blocked && (
          <div className="blocked-banner" data-testid="p1-blocked-note" style={{ marginTop: 10 }}>
            P1 launch controls are hidden: a G-P0 gate failed. The P0 → P1
            transition is blocked by protocol.
          </div>
        )}
      </div>

      <div className="panel" style={{ marginBottom: 14 }}>
        <h2>Gate Rail</h2>
        <GateRail gates={gates} />
      </div>

      <div className="panel" style={{ marginBottom: 14 }}>
        <h2>Live Metrics</h2>
        <MetricCharts metrics={metrics} />
      </div>

      <div className="panel" style={{ marginBottom: 14 }}>
        <h2>Event Log</h2>
        <div className="log" data-testid="event-log">
          {events.map((e) => (
            <div key={e.seq}>
              [{e.seq}] {e.event} {JSON.stringify(e.payload).slice(0, 140)}
            </div>
          ))}
          {events.length === 0 && 'waiting for events…'}
        </div>
      </div>

      <DeviationRegister deviations={[]} />

      <div className="panel" style={{ marginTop: 14 }}>
        <h2>Artifacts</h2>
        <table className="dense">
          <tbody>
            {artifacts.map((a) => (
              <tr key={a.name}>
                <td>{a.name}</td>
                <td>{a.kind}</td>
              </tr>
            ))}
            {artifacts.length === 0 && (
              <tr><td>no artifacts yet</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
