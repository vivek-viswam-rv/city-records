import { useCallback, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { DEFAULT_FROM, PAGE_SIZE } from 'constants/filters'
import useDebouncedValue from 'hooks/useDebouncedValue'
import { todayIso } from 'lib/format'

// filter key (API name) -> URL param
const FILTER_PARAMS = {
  q: 'q',
  agency: 'agency',
  notice_type: 'type',
  product_category: 'category',
  is_software: 'software',
  min_amount: 'min',
}

// Writes `updates` (param -> value | null) onto the current params.
// Null/empty values and values equal to their default are omitted from the URL.
const applyUpdates = (prev, updates, { resetPage }) => {
  const next = new URLSearchParams(prev)
  Object.entries(updates).forEach(([param, value]) => {
    if (value === null || value === undefined || value === '') next.delete(param)
    else next.set(param, value)
  })
  if (resetPage) next.delete('page')
  return next
}

// URL is the single source of truth: everything is parsed from the query string on each render.
// History: filter/range/page changes use `replace` so typing and paging do not spam the back
// button. Only `notice` changes push a history entry, so Back closes the detail panel.
const useUrlFilters = () => {
  const [params, setSearchParams] = useSearchParams()

  const filters = {
    q: params.get('q') || '',
    agency: params.get('agency') || '',
    notice_type: params.get('type') || '',
    product_category: params.get('category') || '',
    is_software: params.get('software') === '1',
    min_amount: params.get('min') || '',
  }
  const range = { from: params.get('from') || DEFAULT_FROM, to: params.get('to') || todayIso() }
  const page = Math.max(1, parseInt(params.get('page'), 10) || 1)
  const offset = (page - 1) * PAGE_SIZE
  const selected = params.get('notice') || null

  const setFilter = useCallback((key, value) => {
    const param = FILTER_PARAMS[key]
    const v = key === 'is_software' ? (value ? '1' : null) : value
    setSearchParams((prev) => applyUpdates(prev, { [param]: v }, { resetPage: true }), { replace: true })
  }, [setSearchParams])

  const setRange = useCallback((partial) => {
    const updates = {}
    if ('from' in partial) updates.from = partial.from === DEFAULT_FROM ? null : partial.from
    if ('to' in partial) updates.to = partial.to === todayIso() ? null : partial.to
    setSearchParams((prev) => applyUpdates(prev, updates, { resetPage: true }), { replace: true })
  }, [setSearchParams])

  const setOffset = useCallback((n) => {
    const p = Math.floor(Math.max(0, n) / PAGE_SIZE) + 1
    setSearchParams((prev) => applyUpdates(prev, { page: p > 1 ? String(p) : null }, { resetPage: false }), { replace: true })
  }, [setSearchParams])

  const setSelected = useCallback((id) => {
    // Opening a notice pushes history (Back closes it); closing replaces, so Back does not reopen it.
    setSearchParams((prev) => applyUpdates(prev, { notice: id ? String(id) : null }, { resetPage: false }), { replace: !id })
  }, [setSearchParams])

  return { filters, range, offset, selected, setFilter, setRange, setOffset, setSelected }
}

// Raw typed value lives in local state so typing stays responsive; the debounced value is
// committed to the URL. External URL changes (back/forward, pasted link) sync into the input.
export const useUrlTextInput = (urlValue, commit) => {
  const [raw, setRaw] = useState(urlValue)
  const debounced = useDebouncedValue(raw)
  const lastCommitted = useRef(urlValue)
  const urlRef = useRef(urlValue)
  const commitRef = useRef(commit)

  useEffect(() => {
    urlRef.current = urlValue
    commitRef.current = commit
  })

  useEffect(() => {
    // Ignore echoes of our own commits so in-flight typing is not overwritten.
    if (urlValue === lastCommitted.current) return
    lastCommitted.current = urlValue
    setRaw(urlValue)
  }, [urlValue])

  useEffect(() => {
    if (debounced === urlRef.current) return
    lastCommitted.current = debounced
    commitRef.current(debounced)
  }, [debounced])

  return [raw, setRaw]
}

export default useUrlFilters
