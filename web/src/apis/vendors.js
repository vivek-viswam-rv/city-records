import axios from 'axios'
import { mockApi, mockResponse, USE_MOCK } from './utils.js'

const show = (id) =>
  USE_MOCK ? mockResponse(() => mockApi.vendor(id)) : axios.get(`/vendors/${encodeURIComponent(id)}`)

export const vendorsApi = { show }

export default vendorsApi
