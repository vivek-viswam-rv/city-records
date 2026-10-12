import { useNotice } from '../lib/api.js'
import { confColor, fmtDate, fmtUsdFull, sourceUrl } from '../lib/format.js'
import { Link } from 'react-router-dom'
import { Chip, TypeBadge } from './ui.jsx'

function Row({ label, children }) {
  if (children == null || children === '') return null
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</dt>
      <dd className="text-sm">{children}</dd>
    </div>
  )
}

export default function NoticeDetail({ id, initial, onClose }) {
  const { data } = useNotice(id)
  const n = data || initial
  const e = n?.enrichment
  return (
    <div className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <TypeBadge type={n.notice_type} />
        <button onClick={onClose} className="rounded-lg px-2 py-1 text-sm text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">
          Close
        </button>
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        <section aria-label="As published">
          <h3 className="mb-2 text-sm font-semibold">As published</h3>
          <h4 className="mb-2 font-medium">{n.title}</h4>
          <p className="mb-3 text-sm text-slate-600 dark:text-slate-300">{n.description}</p>
          <dl className="space-y-2">
            <Row label="Agency">{n.agency}</Row>
            <Row label="Category">{n.category}</Row>
            <Row label="Selection method">{n.selection_method}</Row>
            <Row label="PIN">{n.pin}</Row>
            <Row label="Contact">
              {n.contact_name}
              {n.contact_email && <> · <a className="text-blue-600 underline dark:text-blue-400" href={`mailto:${n.contact_email}`}>{n.contact_email}</a></>}
            </Row>
            <Row label="Amount">{n.contract_amount != null ? fmtUsdFull(n.contract_amount) : null}</Row>
            <Row label="Vendor">
              {n.vendor ? <Link className="text-blue-600 underline dark:text-blue-400" to={`/vendors/${n.vendor.id}`}>{n.vendor.name}</Link> : n.vendor_name_raw}
            </Row>
            <Row label="Published">{fmtDate(n.published_on)}</Row>
            <Row label="End date">{n.end_date ? fmtDate(n.end_date) : null}</Row>
            <Row label="Event date">{n.event_date ? fmtDate(n.event_date) : null}</Row>
          </dl>
          <a className="mt-3 inline-block text-sm text-blue-600 underline dark:text-blue-400" href={sourceUrl(n.request_id)} target="_blank" rel="noreferrer">
            View on City Record Online
          </a>
        </section>
        <section aria-label="Model's reading" className="rounded-lg bg-slate-100 p-3 dark:bg-slate-800/60">
          <h3 className="mb-2 text-sm font-semibold">Model&apos;s reading</h3>
          {!e ? (
            <p className="text-sm text-slate-500">Not enriched yet</p>
          ) : (
            <div className="space-y-3">
              <Row label="What is bought">{e.what_is_bought}</Row>
              <div className="flex flex-wrap gap-1.5">
                <Chip tone="blue">{e.product_category}</Chip>
                {e.is_software && <Chip tone="green">Software</Chip>}
                {e.is_renewal && <Chip tone="amber">Renewal</Chip>}
              </div>
              <Row label="Summary">{e.summary}</Row>
              <div className="flex flex-wrap gap-1.5">{e.keywords?.map((k) => <Chip key={k}>{k}</Chip>)}</div>
              <div>
                <div className="mb-1 text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">Confidence {Math.round(e.confidence * 100)}%</div>
                <div className="h-2 rounded-full bg-slate-300 dark:bg-slate-700" role="progressbar" aria-valuenow={Math.round(e.confidence * 100)} aria-valuemin={0} aria-valuemax={100}>
                  <div className={`h-2 rounded-full ${confColor(e.confidence)}`} style={{ width: `${e.confidence * 100}%` }} />
                </div>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {e.model} · {e.prompt_version} · {fmtDate(e.enriched_at)}
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
