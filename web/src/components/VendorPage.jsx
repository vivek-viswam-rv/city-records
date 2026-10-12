import { Link, useParams } from 'react-router-dom'
import { useVendor } from '../lib/api.js'
import { fmtDate, fmtUsdFull } from '../lib/format.js'
import { TypeBadge, card } from './ui.jsx'

export default function VendorPage() {
  const { id } = useParams()
  const { data, isLoading, error } = useVendor(id)
  return (
    <main className="mx-auto max-w-7xl px-4 py-6">
      <Link to="/" className="text-sm text-blue-600 underline dark:text-blue-400">← All notices</Link>
      {isLoading && <p className="mt-4 text-sm">Loading…</p>}
      {error && <p className="mt-4 text-sm text-red-600">{error.message}</p>}
      {data && (
        <>
          <h1 className="mt-3 text-2xl font-semibold">{data.name}</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">{data.address} · first seen {fmtDate(data.first_seen)}</p>
          <ul className="mt-4 space-y-2">
            {data.notices.map((n) => (
              <li key={n.request_id} className={`${card} p-3`}>
                <div className="flex flex-wrap items-center gap-2">
                  <TypeBadge type={n.notice_type} />
                  <span className="text-xs text-slate-500">{fmtDate(n.published_on)} · {n.agency}</span>
                  <span className="ml-auto text-sm tabular-nums">{fmtUsdFull(n.contract_amount)}</span>
                </div>
                <p className="mt-1 text-sm font-medium">{n.title}</p>
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  )
}
