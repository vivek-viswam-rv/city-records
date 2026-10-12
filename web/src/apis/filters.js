import axios from 'axios'

const fetch = () => axios.get('/filters')

export const filtersApi = { fetch }

export default filtersApi
