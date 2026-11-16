import type { GateOutcome } from '../api'

interface Props {
  gates: GateOutcome[]
}

/**
 * Prominent gate rail: C1–C5 configuration gates followed by G-P0 gates.
 * A failed gate is visually marked (fail color + weight) so an operator can
 * never mistake it for a pass.
 */
export default function GateRail({ gates }: Props) {
  return (
    <div className="gate-rail" data-testid="gate-rail">
      {gates.map((g) => (
        <div key={g.gate_id} className="gate" data-status={g.status} data-gate={g.gate_id}>
          <span className="gate-id">{g.gate_id}</span>
          <span className="gate-msg">{g.message}</span>
          <span className="gate-status">{g.status}</span>
        </div>
      ))}
    </div>
  )
}

export function p0Failed(gates: GateOutcome[]): boolean {
  return gates.some((g) => g.gate_id.startsWith('G-P0') && (g.status === 'fail' || g.status === 'blocked'))
}
