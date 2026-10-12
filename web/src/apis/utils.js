import { mockApi } from '../lib/mock.js'

export const USE_MOCK = import.meta.env.VITE_USE_MOCK === '1'

export const cleanParams = (params = {}) =>
  Object.fromEntries(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== null && v !== '' && v !== false)
      .map(([k, v]) => [k, v === true ? 'true' : v]),
  )

export const mockResponse = (call) => call().then((data) => ({ data }))

export { mockApi }
