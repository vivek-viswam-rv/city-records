import axios from 'axios'
import { cleanParams } from './utils.js'

const fetch = (params) => axios.get('/stats', { params: cleanParams(params) })

export const statsApi = { fetch }

export default statsApi
