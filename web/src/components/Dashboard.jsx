import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useFetchFilters } from 'hooks/reactQuery/useFiltersApi'
import { useFetchNotices } from 'hooks/reactQuery/useNoticesApi'
import useDebouncedValue from 'hooks/useDebouncedValue'
import { fmtDate, fmtUsd, todayIso } from 'lib/format'
import StatsStrip from './StatsStrip.jsx'
import NoticeDetail from './NoticeDetail.jsx'
import { ConfDot, TypeBadge, card, input } from './ui.jsx'

const PAGE = 25

function Select({ label, value, onChange, options }) {
  return (
    <label className="block text-xs text-slate-500 dark:text-slate-400">
      {label}
      <select className={`${input} mt-1`} value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">All</option>
        {options?.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  )
}

export default function Dashboard() {
  const [range, setRange] = useState({ from: '2026-09-01', to: todayIso() })
  const [f, setF] = useState({ q: '', agency: '', notice_type: '', product_category: '', is_software: false, min_amount: '' })
  const [offset, setOffset] = useState(0)
  const [selected, setSelected] = useState(null)

  const set = (k) => (v) => { setF((p) => ({ ...p, [k]: v })); setOffset(0) }
  const debQ = useDebouncedValue(f.q)
  const debMin = useDebouncedValue(f.min_amount)
  const params = useMemo(
    () => ({ ...f, q: debQ, min_amount: debMin, ...range, limit: PAGE, offset }),
    [f, debQ, debMin, range, offset],
  )
  const filters = useFetchFilters()
  const { data, isLoading, error, isFetching } = useFetchNotices(params)
  const items = data?.items || []

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">City Records</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">NYC procurement notices, read daily by a pipeline and an LLM</p>
        </div>
        <div className="flex items-end gap-2 text-xs text-slate-500 dark:text-slate-400">
          <label>From<input type="date" className={`${input} mt-1`} value={range.from} max={range.to} onChange={(e) => { setRange({ ...range, from: e.target.value }); setOffset(0) }} /></label>
          <label>To<input type="date" className={`${input} mt-1`} value={range.to} min={range.from} onChange={(e) => { setRange({ ...range, to: e.target.value }); setOffset(0) }} /></label>
        </div>
      </header>

      <StatsStrip range={range} />

      <section aria-label="Search" className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
        <label className="block text-xs text-slate-500 dark:text-slate-400 sm:col-span-2">
          Search
          <input type="search" className={`${input} mt-1`} placeholder="Title, description, vendor…" value={f.q} onChange={(e) => set('q')(e.target.value)} />
        </label>
        <Select label="Agency" value={f.agency} onChange={set('agency')} options={filters.data?.agencies} />
        <Select label="Notice type" value={f.notice_type} onChange={set('notice_type')} options={filters.data?.notice_types} />
        <Select label="Product category" value={f.product_category} onChange={set('product_category')} options={filters.data?.product_categories} />
        <label className="block text-xs text-slate-500 dark:text-slate-400">
          Min amount ($)
          <input type="number" min="0" step="1000" className={`${input} mt-1`} value={f.min_amount} onChange={(e) => set('min_amount')(e.target.value)} />
        </label>
        <label className="flex items-center gap-2 text-sm sm:col-span-2 lg:col-span-6">
          <input type="checkbox" checked={f.is_software} onChange={(e) => set('is_software')(e.target.checked)} /> Software only
        </label>
      </section>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,28rem)]">
        <section aria-label="Results" className={`${card} overflow-hidden`}>
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-2 text-sm dark:border-slate-800">
            <span>{data ? `${data.total} notices` : 'Loading…'}</span>
            {isFetching && <span className="text-xs text-slate-500">Updating…</span>}
          </div>
          {error && <p className="p-4 text-sm text-red-600">Could not load notices: {error.message}</p>}
          {!isLoading && !error && items.length === 0 && <p className="p-4 text-sm text-slate-500">No notices match.</p>}
          <ul className="divide-y divide-slate-200 dark:divide-slate-800">
            {items.map((n) => (
              <li key={n.request_id}>
                <div
                  role="button"
                  tabIndex={0}
                  onClick={() => setSelected(n)}
                  onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && setSelected(n)}
                  className={`cursor-pointer px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 ${selected?.request_id === n.request_id ? 'bg-blue-50 dark:bg-blue-950/40' : ''}`}
                >
                  <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                    <TypeBadge type={n.notice_type} />
                    <span>{fmtDate(n.published_on)}</span>
                    <span className="truncate">{n.agency}</span>
                    <span className="ml-auto flex items-center gap-2">
                      <ConfDot value={n.enrichment?.confidence} />
                      <span className="text-sm font-medium tabular-nums text-slate-900 dark:text-slate-100">{fmtUsd(n.contract_amount)}</span>
                    </span>
                  </div>
                  <p className="mt-1 text-sm font-medium">{n.title}</p>
                  {n.vendor && (
                    <Link to={`/vendors/${n.vendor.id}`} onClick={(e) => e.stopPropagation()} className="text-xs text-blue-600 underline dark:text-blue-400">
                      {n.vendor.name}
                    </Link>
                  )}
                </div>
              </li>
            ))}
          </ul>
          <div className="flex items-center justify-between border-t border-slate-200 px-4 py-2 text-sm dark:border-slate-800">
            <button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE))} className="rounded-lg border border-slate-300 px-3 py-1 disabled:opacity-40 dark:border-slate-700">Previous</button>
            <span className="text-xs text-slate-500">{data && data.total > 0 ? `${offset + 1}–${offset + items.length}` : ''}</span>
            <button disabled={!data?.has_more} onClick={() => setOffset(offset + PAGE)} className="rounded-lg border border-slate-300 px-3 py-1 disabled:opacity-40 dark:border-slate-700">Next</button>
          </div>
        </section>

        <aside
          aria-label="Notice detail"
          className={`${selected ? '' : 'hidden lg:block'} fixed inset-x-0 bottom-0 top-12 z-40 overflow-auto rounded-t-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900 lg:sticky lg:inset-auto lg:top-4 lg:z-auto lg:max-h-[calc(100vh-2rem)] lg:self-start lg:rounded-xl lg:shadow-none`}
        >
          {selected ? (
            <NoticeDetail key={selected.request_id} id={selected.request_id} initial={selected} onClose={() => setSelected(null)} />
          ) : (
            <p className="p-4 text-sm text-slate-500">Select a notice to see it as published next to the model&apos;s reading.</p>
          )}
        </aside>
      </div>
    </div>
  )
}
