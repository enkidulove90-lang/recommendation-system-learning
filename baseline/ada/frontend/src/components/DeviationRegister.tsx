interface Deviation {
  code: string
  level: string
  description: string
  handling: string
}

interface Props {
  deviations: Deviation[]
}

const LEVEL_COLOR: Record<string, string> = {
  high: 'var(--signal-fail)',
  mid: 'var(--signal-warn)',
  low: 'var(--signal-ok)',
  conditional: 'var(--signal-blocked)',
}

export default function DeviationRegister({ deviations }: Props) {
  return (
    <div className="panel" data-testid="deviation-register">
      <h2>Deviation Register</h2>
      <table className="dense">
        <thead>
          <tr>
            <th>Code</th>
            <th>Level</th>
            <th>Description</th>
            <th>Handling</th>
          </tr>
        </thead>
        <tbody>
          {deviations.map((d) => (
            <tr key={d.code}>
              <td>{d.code}</td>
              <td style={{ color: LEVEL_COLOR[d.level] ?? 'var(--text-dim)' }}>{d.level}</td>
              <td>{d.description}</td>
              <td>{d.handling}</td>
            </tr>
          ))}
          {deviations.length === 0 && (
            <tr>
              <td colSpan={4}>no deviations registered</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
