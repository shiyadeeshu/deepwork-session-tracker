import { useState } from 'react'
import { errorMessage, sessionsApi } from '../api/client'

const PRESETS = [25, 50, 90]
const EMPTY = { title: '', goal: '', duration: '50' }

export default function SessionForm({ onCreated }) {
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  // Client-side checks mirror the API's validation; the API remains the source of truth.
  function validate() {
    const minutes = Number(form.duration)
    if (!form.title.trim()) return 'Title is required.'
    if (!Number.isInteger(minutes) || minutes < 1 || minutes > 1440)
      return 'Duration must be a whole number of minutes between 1 and 1440.'
    return null
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const problem = validate()
    if (problem) return setError(problem)

    setSaving(true)
    setError(null)
    try {
      const created = await sessionsApi.create({
        title: form.title.trim(),
        goal: form.goal.trim(),
        scheduled_duration: Number(form.duration),
      })
      setForm(EMPTY)
      onCreated?.(created)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <h2>Schedule a session</h2>
      <div className="form-row">
        <label>
          Title *
          <input value={form.title} onChange={set('title')} maxLength={200}
            placeholder="Write report intro" required />
        </label>
        <label>
          Goal
          <input value={form.goal} onChange={set('goal')} maxLength={1000}
            placeholder="Finish the first draft" />
        </label>
        <label>
          Minutes *
          <input type="number" min={1} max={1440} step={1}
            value={form.duration} onChange={set('duration')} required />
        </label>
        <button type="submit" className="primary" disabled={saving}>
          {saving ? 'Saving…' : 'Schedule'}
        </button>
      </div>
      <div className="presets" aria-label="Duration presets">
        {PRESETS.map((m) => (
          <button type="button" key={m} onClick={() => setForm((f) => ({ ...f, duration: String(m) }))}>
            {m} min
          </button>
        ))}
      </div>
      {error && <div className="error" role="alert">{error}</div>}
    </form>
  )
}
