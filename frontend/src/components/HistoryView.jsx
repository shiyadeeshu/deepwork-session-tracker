import {
  Bar, BarChart, CartesianGrid, LabelList, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { sessionsApi } from '../api/client'
import { usePolling } from '../hooks/usePolling'
import { formatDateTime, formatMinutes, formatPercent } from '../format'
import StatusBadge from './StatusBadge'

// Final outcomes use the reserved status colors; each bar is also labelled on the axis.
const OUTCOMES = [
  { status: 'completed', color: 'var(--good)' },
  { status: 'overdue', color: 'var(--warning)' },
  { status: 'abandoned', color: 'var(--serious)' },
  { status: 'interrupted', color: 'var(--critical)' },
]

const AXIS = { stroke: 'var(--axis)', tick: { fill: 'var(--muted)', fontSize: 12 }, tickLine: false }

function Stat({ label, value, sub }) {
  return (
    <div className="card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  )
}

function ChartTooltip({ active, payload, label, titleFor }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <strong>{titleFor ? titleFor(payload[0].payload) : label}</strong>
      {payload.map((p) => (
        <div className="row" key={p.dataKey}>
          <span className="key" style={{ background: p.color ?? p.payload.color }} />
          {p.name}: {p.dataKey === 'count' ? p.value : formatMinutes(p.value)}
        </div>
      ))}
    </div>
  )
}

function OutcomeChart({ counts }) {
  const data = OUTCOMES.map((o) => ({ ...o, count: counts[o.status] ?? 0 }))
  return (
    <div className="card">
      <h3 className="chart-title">Session outcomes</h3>
      <div className="chart-box">
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 20, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--grid)" />
            <XAxis dataKey="status" {...AXIS} tickFormatter={(s) => s[0].toUpperCase() + s.slice(1)} />
            <YAxis allowDecimals={false} {...AXIS} axisLine={false} />
            <Tooltip cursor={{ fill: 'var(--surface-2)' }} content={<ChartTooltip />} />
            <Bar dataKey="count" name="Sessions" radius={[4, 4, 0, 0]} maxBarSize={48}
              isAnimationActive={false}
              shape={(props) => <rect {...props} fill={props.payload.color} rx={4} />}>
              <LabelList dataKey="count" position="top" fill="var(--ink-2)" fontSize={12} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function DurationChart({ sessions }) {
  // Oldest -> newest, last 10 finished sessions.
  const data = sessions.slice(0, 10).reverse().map((s) => ({
    label: `#${s.id}`,
    title: s.title,
    planned: s.scheduled_duration,
    actual: s.actual_duration_minutes ?? 0,
  }))
  return (
    <div className="card">
      <h3 className="chart-title">Planned vs actual minutes (last {data.length})</h3>
      <div className="chart-box">
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }} barGap={2}>
            <CartesianGrid vertical={false} stroke="var(--grid)" />
            <XAxis dataKey="label" {...AXIS} />
            <YAxis {...AXIS} axisLine={false} />
            <Tooltip cursor={{ fill: 'var(--surface-2)' }}
              content={<ChartTooltip titleFor={(d) => `${d.label} · ${d.title}`} />} />
            <Legend iconType="square" iconSize={10} itemSorter={null}
              formatter={(v) => <span style={{ color: 'var(--ink-2)', fontSize: 12 }}>{v}</span>} />
            <Bar dataKey="planned" name="Planned" fill="var(--series-1)" radius={[4, 4, 0, 0]}
              maxBarSize={22} isAnimationActive={false} />
            <Bar dataKey="actual" name="Actual" fill="var(--series-2)" radius={[4, 4, 0, 0]}
              maxBarSize={22} isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function HistoryView() {
  const { data, error, loading } = usePolling(sessionsApi.history, 10000)

  if (loading && !data) return <div className="empty">Loading history…</div>
  if (!data) return <div className="error banner" role="alert">{error}</div>

  const c = data.status_counts
  return (
    <div className="stack">
      {error && <div className="error banner" role="alert">{error}</div>}

      <div className="stats">
        <Stat label="Completion ratio" value={formatPercent(data.completion_ratio)}
          sub={`${c.completed} of ${data.finished_sessions} finished`} />
        <Stat label="Focus time" value={formatMinutes(data.total_focus_minutes)}
          sub="across finished sessions" />
        <Stat label="Avg. session" value={formatMinutes(data.average_duration_minutes)} />
        <Stat label="Total pauses" value={data.total_pauses}
          sub={`${data.average_pauses_per_session.toFixed(2)} per session`} />
        <Stat label="Sessions" value={data.total_sessions}
          sub={`${c.scheduled} scheduled · ${c.active + c.paused} in progress`} />
      </div>

      {data.finished_sessions > 0 && (
        <div className="charts">
          <OutcomeChart counts={c} />
          <DurationChart sessions={data.sessions} />
        </div>
      )}

      <section className="card">
        <h2>Past sessions</h2>
        {data.sessions.length === 0 ? (
          <div className="empty">No finished sessions yet.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Session</th><th>Status</th><th className="num">Planned</th>
                  <th className="num">Actual</th><th className="num">Pauses</th>
                  <th>Interruptions</th><th>Started</th>
                </tr>
              </thead>
              <tbody>
                {data.sessions.map((s) => (
                  <tr key={s.id}>
                    <td><strong>{s.title}</strong>{s.goal && <div className="reasons">{s.goal}</div>}</td>
                    <td><StatusBadge status={s.status} /></td>
                    <td className="num">{s.scheduled_duration} min</td>
                    <td className="num">{formatMinutes(s.actual_duration_minutes)}</td>
                    <td className="num">{s.pause_count}</td>
                    <td className="reasons">{s.interruptions.map((i) => i.reason).join(', ') || '—'}</td>
                    <td>{formatDateTime(s.start_time)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
