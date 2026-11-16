import type { MetricSeries } from '../api'

interface Props {
  metrics: MetricSeries
}

const SERIES: { key: keyof MetricSeries; label: string }[] = [
  { key: 'loss', label: 'Loss' },
  { key: 'codebook_usage', label: 'Codebook usage' },
  { key: 'grad_norm', label: 'Grad norm' },
  { key: 'memory_mb', label: 'Memory (MB)' },
  { key: 'step_ms', label: 'Step time (ms)' },
  { key: 'valid_metric', label: 'Valid metric' },
]

const W = 260
const H = 80

/**
 * Metric charts that preserve the distinction between "no metric emitted"
 * (a gap in the series) and a zero value (a real point at 0).
 *
 * A ``null``/missing entry is rendered as a data-missing marker and breaks
 * the line; a genuine zero renders as a real point on the baseline.
 */
export default function MetricCharts({ metrics }: Props) {
  return (
    <div className="charts">
      {SERIES.map(({ key, label }) => {
        const data = (metrics[key] ?? []) as (number | null)[]
        return <SingleChart key={key} label={label} data={data} />
      })}
    </div>
  )
}

export function SingleChart({ label, data }: { label: string; data: (number | null)[] }) {
  const finite = data.filter((v): v is number => v !== null && Number.isFinite(v))
  const max = finite.length ? Math.max(...finite) : 1
  const min = finite.length ? Math.min(...finite) : 0
  const span = max - min || 1
  const n = data.length || 1
  const x = (i: number) => (i / Math.max(n - 1, 1)) * (W - 8) + 4
  const y = (v: number) => H - 8 - ((v - min) / span) * (H - 16)

  // Build contiguous polyline segments across non-null runs.
  const segments: string[] = []
  let current: string[] = []
  data.forEach((v, i) => {
    if (v === null || !Number.isFinite(v)) {
      if (current.length > 1) segments.push(current.join(' '))
      current = []
    } else {
      current.push(`${current.length === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(v).toFixed(1)}`)
    }
  })
  if (current.length > 1) segments.push(current.join(' '))

  const missingCount = data.filter((v) => v === null || !Number.isFinite(v)).length

  return (
    <div className="chart" data-testid={`chart-${label}`}>
      <h3>{label}</h3>
      <svg width={W} height={H} data-missing-count={missingCount} role="img" aria-label={label}>
        {segments.map((d, i) => (
          <path key={i} d={d} fill="none" stroke="var(--signal-pass)" strokeWidth="1.5" />
        ))}
        {data.map((v, i) =>
          v === null || !Number.isFinite(v) ? (
            <rect
              key={`gap-${i}`}
              x={x(i) - 2}
              y={4}
              width={4}
              height={H - 8}
              fill="rgba(255,255,255,0.06)"
              data-missing="true"
            />
          ) : (
            <circle key={`pt-${i}`} cx={x(i)} cy={y(v)} r={1.8} fill="var(--signal-ok)" />
          ),
        )}
      </svg>
      <div className="chart-meta">
        {data.length === 0 ? 'no metric emitted' : `${finite.length}/${data.length} points`}
      </div>
    </div>
  )
}
