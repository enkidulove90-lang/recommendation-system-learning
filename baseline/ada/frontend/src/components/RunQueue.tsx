import type { RunRecord } from '../api'

interface Props {
  runs: RunRecord[]
  onSelect: (runId: string) => void
}

export default function RunQueue({ runs, onSelect }: Props) {
  return (
    <div className="panel" data-testid="run-queue">
      <h2>Run Queue</h2>
      <table className="dense">
        <thead>
          <tr>
            <th>Run</th>
            <th>Phase</th>
            <th>Status</th>
            <th>PID</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((r) => (
            <tr key={r.run_id} onClick={() => onSelect(r.run_id)} style={{ cursor: 'pointer' }}>
              <td>{r.run_id}</td>
              <td>{r.phase}</td>
              <td>
                <span className={`status-chip ${r.status}`}>{r.status}</span>
              </td>
              <td>{r.pid ?? '—'}</td>
            </tr>
          ))}
          {runs.length === 0 && (
            <tr>
              <td colSpan={4}>no runs yet</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
