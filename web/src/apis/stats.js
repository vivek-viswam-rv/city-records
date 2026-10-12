import axios from 'axios'
import { cleanParams, mockApi, mockResponse, USE_MOCK } from './utils.js'

const fetch = (params) =>
  USE_MOCK ? mockResponse(() => mockApi.stats(params)) : axios.get('/stats', { params: cleanParams(params) })

export const statsApi = { fetch }

export default statsApi
