import axios from 'axios'
import { cleanParams, mockApi, mockResponse, USE_MOCK } from './utils.js'

const fetch = (params) =>
  USE_MOCK ? mockResponse(() => mockApi.notices(params)) : axios.get('/notices', { params: cleanParams(params) })

const show = (id) =>
  USE_MOCK ? mockResponse(() => mockApi.notice(id)) : axios.get(`/notices/${encodeURIComponent(id)}`)

export const noticesApi = { fetch, show }

export default noticesApi
