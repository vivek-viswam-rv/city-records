import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useFetchStats } from 'hooks/reactQuery/useStatsApi'
import { fmtInt, fmtUsd, TYPE_COLORS } from 'lib/format'
import { card } from './ui.jsx'

function Tile({ label, value }) {
  return (
    <div className={`${card} p-4`}>
      <div className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</div>
      <div className="mt-1 text-2xl font-semibold tabular-nums">{value}</div>
    </div>
  )
}

function pivot(byWeek) {
  const rows = {}
  byWeek.forEach(({ week, notice_type, usd }) => {
    rows[week] = rows[week] || { week }
    rows[week][notice_type] = (rows[week][notice_type] || 0) + usd
  })
  return Object.values(rows).sort((a, b) => a.week.localeCompare(b.week))
}

export default function StatsStrip({ range }) {
  const { data, isLoading, error } = useFetchStats(range)
  if (error) return <p className="text-sm text-red-600">Could not load stats: {error.message}</p>
  const s = data
  const types = s ? [...new Set(s.by_week.map((w) => w.notice_type))] : []
  return (
    <section aria-label="Summary" className="space-y-3">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Tile label="Notices" value={s ? fmtInt(s.notices) : '…'} />
        <Tile label="Solicitations, last 30 days" value={s ? fmtInt(s.open_solicitations) : '…'} />
        <Tile label="Awarded" value={s ? fmtUsd(s.awarded_usd) : '…'} />
        <Tile label="Vendors" value={s ? fmtInt(s.vendors) : '…'} />
      </div>
      <div className={`${card} p-4`}>
        <h2 className="mb-2 text-sm font-medium">Weekly value by notice type</h2>
        <div className="h-56">
          {isLoading ? null : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={pivot(s.by_week)} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" strokeOpacity={0.3} />
                <XAxis dataKey="week" tick={{ fontSize: 11 }} tickFormatter={(w) => w.slice(5)} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={fmtUsd} width={52} />
                <Tooltip formatter={(v) => fmtUsd(v)} contentStyle={{ fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                {types.map((t) => (
                  <Bar key={t} dataKey={t} stackId="a" fill={TYPE_COLORS[t] || '#64748b'} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </section>
  )
}
