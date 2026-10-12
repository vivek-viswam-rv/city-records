const compact = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 1 })
const full = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

export const fmtUsd = (n) => (n == null ? '—' : compact.format(n))
export const fmtUsdFull = (n) => (n == null ? '—' : full.format(n))
export const fmtInt = (n) => (n == null ? '—' : new Intl.NumberFormat('en-US').format(n))
export const fmtDate = (d) => {
  if (!d) return '—'
  const dt = new Date(d.length === 10 ? d + 'T00:00:00' : d)
  return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
export const todayIso = () => new Date().toISOString().slice(0, 10)
export const sourceUrl = (id) => `https://a856-cityrecord.nyc.gov/RequestDetail/${id}`

export const TYPE_STYLES = {
  Award: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200',
  Solicitation: 'bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-200',
  'Intent to Award': 'bg-violet-100 text-violet-800 dark:bg-violet-900/50 dark:text-violet-200',
  'Public Hearings': 'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-200',
}
export const TYPE_COLORS = {
  Award: '#10b981',
  Solicitation: '#0ea5e9',
  'Intent to Award': '#8b5cf6',
  'Public Hearings': '#f59e0b',
}
export const confColor = (c) => (c == null ? 'bg-slate-400' : c >= 0.8 ? 'bg-emerald-500' : c >= 0.5 ? 'bg-amber-500' : 'bg-red-500')
