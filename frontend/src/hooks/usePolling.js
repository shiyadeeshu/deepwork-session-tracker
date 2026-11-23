import { useCallback, useEffect, useState } from 'react'
import { errorMessage } from '../api/client'

/**
 * Fetches data now and every `intervalMs` (real-time-ish updates, e.g. a session
 * turning "abandoned" on the server). Skips polling while the tab is hidden.
 * `fetcher` should be a stable function (e.g. from sessionsApi).
 * Returns { data, error, loading, refresh }.
 */
export function usePolling(fetcher, intervalMs = 5000) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    try {
      setData(await fetcher())
      setError(null)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [fetcher])

  useEffect(() => {
    refresh()
    const id = setInterval(() => {
      if (document.visibilityState === 'visible') refresh()
    }, intervalMs)
    const onVisible = () => document.visibilityState === 'visible' && refresh()
    document.addEventListener('visibilitychange', onVisible)
    return () => {
      clearInterval(id)
      document.removeEventListener('visibilitychange', onVisible)
    }
  }, [refresh, intervalMs])

  return { data, error, loading, refresh }
}
