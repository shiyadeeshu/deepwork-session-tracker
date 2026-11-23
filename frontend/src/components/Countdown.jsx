import { useNow } from '../hooks/useNow'
import { OVERDUE_TOLERANCE, formatClock } from '../format'

/**
 * Live countdown for an active/paused session.
 * Mirrors the backend rule: time is wall-clock from start (pauses included),
 * and completing after duration * 1.1 makes the session overdue.
 */
export default function Countdown({ session }) {
  const now = useNow(1000)
  const start = new Date(session.start_time).getTime()
  const plannedMs = session.scheduled_duration * 60_000
  const graceMs = plannedMs * (1 + OVERDUE_TOLERANCE)

  const elapsed = now - start
  const remaining = (plannedMs - elapsed) / 1000
  const paused = session.status === 'paused'

  let state = 'ok'
  let label = paused ? 'Paused · the clock keeps running' : 'Remaining'
  if (elapsed > graceMs) {
    state = 'late'
    label = paused
      ? 'Allowed time used up · will be marked abandoned'
      : 'Past the 10% grace period · completing now = overdue'
  } else if (elapsed > plannedMs) {
    state = 'over'
    label = `Over time · finish within ${formatClock((graceMs - elapsed) / 1000)} to avoid overdue`
  }

  const pct = Math.min(100, Math.max(0, (elapsed / plannedMs) * 100))

  return (
    <div className={`countdown ${state} ${paused ? 'paused' : ''}`} aria-live="off">
      <div className="countdown-time">{formatClock(remaining)}</div>
      <div className="countdown-label">{label}</div>
      <div className="progress" role="progressbar" aria-valuenow={Math.round(pct)}
        aria-valuemin={0} aria-valuemax={100} aria-label="Session progress">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
