import axios from 'axios'
import { cleanParams } from './utils.js'

const fetch = (params) => axios.get('/notices', { params: cleanParams(params) })

const show = (id) => axios.get(`/notices/${encodeURIComponent(id)}`)

export const noticesApi = { fetch, show }

export default noticesApi
