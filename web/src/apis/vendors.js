import axios from 'axios'

const show = (id) => axios.get(`/vendors/${encodeURIComponent(id)}`)

export const vendorsApi = { show }

export default vendorsApi
