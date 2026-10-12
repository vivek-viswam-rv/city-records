import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { mockApi } from './mock.js'

const BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')
const KEY = import.meta.env.VITE_API_KEY
export const USE_MOCK = import.meta.env.VITE_USE_MOCK === '1'

function qs(params = {}) {
  const sp = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '' && v !== false) sp.set(k, v === true ? 'true' : v)
  })
  const s = sp.toString()
  return s ? `?${s}` : ''
}

async function get(path, params) {
  const res = await fetch(`${BASE}${path}${qs(params)}`, {
    headers: KEY ? { 'x-api-key': KEY } : {},
  })
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`)
  return res.json()
}

export const api = {
  notices: (p) => (USE_MOCK ? mockApi.notices(p) : get('/notices', p)),
  notice: (id) => (USE_MOCK ? mockApi.notice(id) : get(`/notices/${encodeURIComponent(id)}`)),
  vendor: (id) => (USE_MOCK ? mockApi.vendor(id) : get(`/vendors/${encodeURIComponent(id)}`)),
  stats: (p) => (USE_MOCK ? mockApi.stats(p) : get('/stats', p)),
  filters: () => (USE_MOCK ? mockApi.filters() : get('/filters')),
}

export const useNotices = (p) => useQuery({ queryKey: ['notices', p], queryFn: () => api.notices(p), placeholderData: keepPreviousData })
export const useNotice = (id) => useQuery({ queryKey: ['notice', id], queryFn: () => api.notice(id), enabled: !!id })
export const useVendor = (id) => useQuery({ queryKey: ['vendor', id], queryFn: () => api.vendor(id) })
export const useStats = (p) => useQuery({ queryKey: ['stats', p], queryFn: () => api.stats(p) })
export const useFilters = () => useQuery({ queryKey: ['filters'], queryFn: api.filters, staleTime: 600_000 })
