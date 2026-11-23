import { useState } from 'react'
import { errorMessage, sessionsApi } from '../api/client'
import { formatDateTime } from '../format'
import Countdown from './Countdown'
import StatusBadge from './StatusBadge'

const MAX_PAUSES = 3 // mirrors backend: the 4th pause interrupts the session

export default function SessionCard({ session, onChanged }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [pausing, setPausing] = useState(false)
  const [reason, setReason] = useState('')

  const { id, status, pause_count: pauses } = session

  async function run(action) {
    setBusy(true)
    setError(null)
    try {
      const updated = await action()
      setPausing(false)
      setReason('')
      onChanged?.(updated)
    } catch (err) {
      setError(errorMessage(err))
      onChanged?.() // refresh: the server may have changed status (e.g. abandoned)
    } finally {
      setBusy(false)
    }
  }

  function submitPause(e) {
    e.preventDefault()
    if (!reason.trim()) return setError('Please enter a reason for the interruption.')
    run(() => sessionsApi.pause(id, reason.trim()))
  }

  function complete() {
    if (status === 'paused' &&
        !window.confirm('This session was never resumed, so it will be marked ABANDONED. Continue?')) {
      return
    }
    run(() => sessionsApi.complete(id))
  }

  return (
    <article className="card">
      <div className="session-head">
        <div>
          <h3>{session.title}</h3>
          {session.goal && <p className="session-goal">{session.goal}</p>}
        </div>
        <StatusBadge status={status} />
      </div>

      <div className="meta">
        <span>{session.scheduled_duration} min planned</span>
        <span>Pauses: {pauses}/{MAX_PAUSES}</span>
        {session.start_time && <span>Started {formatDateTime(session.start_time)}</span>}
      </div>

      {(status === 'active' || status === 'paused') && session.start_time && (
        <Countdown session={session} />
      )}

      {pausing ? (
        <form className="pause-form" onSubmit={submitPause}>
          <input autoFocus value={reason} onChange={(e) => setReason(e.target.value)}
            maxLength={500} placeholder="Why are you pausing? e.g. Phone call"
            aria-label="Interruption reason" />
          <button type="submit" className="primary" disabled={busy}>Pause</button>
          <button type="button" onClick={() => { setPausing(false); setError(null) }}>Cancel</button>
        </form>
      ) : (
        <div className="actions">
          {status === 'scheduled' && (
            <button className="primary" disabled={busy} onClick={() => run(() => sessionsApi.start(id))}>
              Start
            </button>
          )}
          {status === 'active' && (
            <>
              <button disabled={busy} onClick={() => setPausing(true)}>Pause</button>
              <button className="primary" disabled={busy} onClick={complete}>Complete</button>
            </>
          )}
          {status === 'paused' && (
            <>
              <button className="primary" disabled={busy} onClick={() => run(() => sessionsApi.resume(id))}>
                Resume
              </button>
              <button className="danger" disabled={busy} onClick={complete}>Complete</button>
            </>
          )}
        </div>
      )}

      {status === 'active' && pauses === MAX_PAUSES && (
        <p className="warn-hint">⚠ You have used all {MAX_PAUSES} pauses. Pausing again marks this session interrupted.</p>
      )}

      {pauses > 0 && (
        <details className="interruptions">
          <summary>Interruptions ({pauses})</summary>
          <ol>
            {session.interruptions.map((i) => (
              <li key={i.id}>{i.reason} <span className="count">· {formatDateTime(i.pause_time)}</span></li>
            ))}
          </ol>
        </details>
      )}

      {error && <div className="error" role="alert">{error}</div>}
    </article>
  )
}
