import { useQuery } from '@tanstack/react-query'
import statsApi from 'apis/stats'
import { QUERY_KEYS } from 'constants/query'

export const useFetchStats = (params) =>
  useQuery({
    queryKey: [QUERY_KEYS.STATS, params],
    queryFn: () => statsApi.fetch(params),
    select: (response) => response.data,
  })
