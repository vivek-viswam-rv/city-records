import axios from 'axios'
import { BASE_URL } from './constants.js'

axios.defaults.baseURL = BASE_URL
axios.defaults.headers.common.Accept = 'application/json'
if (import.meta.env.VITE_API_KEY) {
  axios.defaults.headers.common['x-api-key'] = import.meta.env.VITE_API_KEY
}

export const registerIntercepts = () => {
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      const detail = error.response?.data?.detail
      const status = error.response?.status
      const message = status
        ? `API ${status}: ${typeof detail === 'string' ? detail : error.response.statusText}`
        : error.message
      return Promise.reject(new Error(message))
    },
  )
}
