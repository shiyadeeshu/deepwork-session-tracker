// Shared formatting helpers + status metadata.

export const OVERDUE_TOLERANCE = 0.1 // mirrors backend: finish within +10%

export const STATUSES = [
  'scheduled', 'active', 'paused', 'completed', 'interrupted', 'abandoned', 'overdue',
]
export const FINISHED = new Set(['completed', 'interrupted', 'abandoned', 'overdue'])

/** Seconds -> "1:05:09" / "25:03". Negative values get a leading "-". */
export function formatClock(totalSeconds) {
  const sign = totalSeconds < 0 ? '-' : ''
  const s = Math.floor(Math.abs(totalSeconds))
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = String(s % 60).padStart(2, '0')
  return h ? `${sign}${h}:${String(m).padStart(2, '0')}:${sec}` : `${sign}${m}:${sec}`
}

export function formatMinutes(min) {
  if (min == null) return '—'
  return `${Math.round(min * 10) / 10} min`
}

export function formatDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

export function formatPercent(ratio) {
  return `${Math.round(ratio * 100)}%`
}
