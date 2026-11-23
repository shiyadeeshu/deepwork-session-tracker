import { lazy, Suspense, useEffect, useState } from 'react'
import SessionsView from './components/SessionsView'

// Charts (Recharts) are only downloaded when the History tab is opened.
const HistoryView = lazy(() => import('./components/HistoryView'))

const TABS = { sessions: 'Sessions', history: 'History' }

const tabFromHash = () => (window.location.hash.slice(1) in TABS ? window.location.hash.slice(1) : 'sessions')

export default function App() {
  // The active tab lives in the URL hash (#history), so it survives reloads and can be linked.
  const [tab, setTabState] = useState(tabFromHash)
  const setTab = (key) => { window.location.hash = key }

  useEffect(() => {
    const onHash = () => setTabState(tabFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  return (
    <>
      <header className="app-header">
        <div>
          <h1>Deep Work Tracker</h1>
          <p className="subtitle">Plan focused sessions, log interruptions, reflect on your stats.</p>
        </div>
        <nav className="tabs" role="tablist">
          {Object.entries(TABS).map(([key, label]) => (
            <button key={key} role="tab" aria-selected={tab === key} onClick={() => setTab(key)}>
              {label}
            </button>
          ))}
        </nav>
      </header>
      <main>
        {tab === 'sessions' ? (
          <SessionsView />
        ) : (
          <Suspense fallback={<div className="empty">Loading history…</div>}>
            <HistoryView />
          </Suspense>
        )}
      </main>
    </>
  )
}
