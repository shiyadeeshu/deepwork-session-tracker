// All backend communication goes through this module (Axios only, no direct DB access).
import axios from 'axios'

export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const http = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

/** Turn any Axios error into a human-readable message. */
export function errorMessage(err) {
  if (!err.response) {
    return `Cannot reach the API at ${API_URL}. Is the backend running?`
  }
  const { detail } = err.response.data ?? {}
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    // FastAPI 422 validation errors: [{loc: [...], msg: '...'}]
    return detail.map((d) => `${d.loc?.at(-1) ?? 'field'}: ${d.msg}`).join('; ')
  }
  return `Request failed (${err.response.status})`
}

const data = (promise) => promise.then((r) => r.data)

export const sessionsApi = {
  list: () => data(http.get('/sessions/')),
  get: (id) => data(http.get(`/sessions/${id}`)),
  history: () => data(http.get('/sessions/history')),
  create: ({ title, goal, scheduled_duration }) =>
    data(http.post('/sessions/', { title, goal: goal || null, scheduled_duration })),
  start: (id) => data(http.patch(`/sessions/${id}/start`)),
  pause: (id, reason) => data(http.patch(`/sessions/${id}/pause`, { reason })),
  resume: (id) => data(http.patch(`/sessions/${id}/resume`)),
  complete: (id) => data(http.patch(`/sessions/${id}/complete`)),
}
