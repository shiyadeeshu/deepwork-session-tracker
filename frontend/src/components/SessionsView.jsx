import { sessionsApi } from '../api/client'
import { usePolling } from '../hooks/usePolling'
import SessionCard from './SessionCard'
import SessionForm from './SessionForm'

function Group({ title, sessions, onChanged, emptyText }) {
  return (
    <section>
      <div className="section-title">
        <h2>{title}</h2>
        <span className="count">{sessions.length}</span>
      </div>
      {sessions.length === 0 ? (
        <div className="empty">{emptyText}</div>
      ) : (
        <div className="grid">
          {sessions.map((s) => <SessionCard key={s.id} session={s} onChanged={onChanged} />)}
        </div>
      )}
    </section>
  )
}

export default function SessionsView() {
  // Poll so server-side status changes (e.g. lazily-detected "abandoned") show up live.
  const { data, error, loading, refresh } = usePolling(sessionsApi.list, 5000)
  const sessions = data ?? []

  const inProgress = sessions.filter((s) => s.status === 'active' || s.status === 'paused')
  const scheduled = sessions.filter((s) => s.status === 'scheduled')

  return (
    <div className="stack">
      <SessionForm onCreated={refresh} />
      {error && <div className="error banner" role="alert">{error}</div>}
      {loading && !data ? (
        <div className="empty">Loading sessions…</div>
      ) : (
        <>
          <Group title="In progress" sessions={inProgress} onChanged={refresh}
            emptyText="Nothing running. Start a scheduled session below." />
          <Group title="Scheduled" sessions={scheduled} onChanged={refresh}
            emptyText="No scheduled sessions. Plan one above." />
          <p className="hint">Finished sessions appear in the History tab.</p>
        </>
      )}
    </div>
  )
}
