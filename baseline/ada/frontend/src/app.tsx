import { useState } from 'react'
import RunQueue from './components/RunQueue'
import ProtocolPage from './pages/ProtocolPage'
import RunDetailPage from './pages/RunDetailPage'
import { api, type RunRecord } from './api'
import { useEffect } from 'react'

type View = { page: 'protocol' } | { page: 'detail'; runId: string }

export default function App() {
  const [view, setView] = useState<View>({ page: 'protocol' })
  const [runs, setRuns] = useState<RunRecord[]>([])

  const refresh = () => {
    api
      .listRuns()
      .then((r) => setRuns(r.runs))
      .catch(() => setRuns([]))
  }

  useEffect(() => {
    refresh()
    const t = setInterval(refresh, 3000)
    return () => clearInterval(t)
  }, [view])

  return (
    <div>
      <header className="app-header">
        <h1>ADA · Experiment Console</h1>
        <span className="sub">protocol-gated P0 → P1 → P2 scaffold · no benchmark claims</span>
        <nav style={{ marginLeft: 'auto' }}>
          <button className="btn" onClick={() => setView({ page: 'protocol' })}>
            Protocol
          </button>
        </nav>
      </header>
      <div className="layout">
        <aside style={{ width: 420, flexShrink: 0 }}>
          <RunQueue runs={runs} onSelect={(runId) => setView({ page: 'detail', runId })} />
        </aside>
        <main style={{ flex: 1, minWidth: 0 }}>
          {view.page === 'protocol' ? (
            <ProtocolPage
              onCreated={(runId) => setView({ page: 'detail', runId })}
            />
          ) : (
            <RunDetailPage runId={view.runId} />
          )}
        </main>
      </div>
    </div>
  )
}
