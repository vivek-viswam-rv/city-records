import axios from 'axios'
import { mockApi, mockResponse, USE_MOCK } from './utils.js'

const fetch = () => (USE_MOCK ? mockResponse(() => mockApi.filters()) : axios.get('/filters'))

export const filtersApi = { fetch }

export default filtersApi
