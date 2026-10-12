import { TYPE_STYLES, confColor } from '../lib/format.js'

export function TypeBadge({ type }) {
  return (
    <span className={`inline-block whitespace-nowrap rounded-full px-2 py-0.5 text-xs font-medium ${TYPE_STYLES[type] || 'bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-100'}`}>
      {type}
    </span>
  )
}

export function ConfDot({ value }) {
  const label = value == null ? 'Not enriched' : `Confidence ${Math.round(value * 100)}%`
  return <span title={label} aria-label={label} role="img" className={`inline-block h-2.5 w-2.5 rounded-full ${confColor(value)}`} />
}

export function Chip({ children, tone = 'slate' }) {
  const tones = {
    slate: 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-200',
    blue: 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-200',
    amber: 'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-200',
    green: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200',
  }
  return <span className={`inline-block rounded-md px-2 py-0.5 text-xs ${tones[tone]}`}>{children}</span>
}

export const card = 'rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900'
export const input = 'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900'
