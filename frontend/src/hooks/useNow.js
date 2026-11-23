import { useEffect, useState } from 'react'

/** Current time (ms), re-rendering every `tickMs`. Used by the live countdown. */
export function useNow(tickMs = 1000) {
  const [now, setNow] = useState(() => Date.now())
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), tickMs)
    return () => clearInterval(id)
  }, [tickMs])
  return now
}
