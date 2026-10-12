import { useQuery } from '@tanstack/react-query'
import filtersApi from 'apis/filters'
import { QUERY_KEYS } from 'constants/query'

export const useFetchFilters = () =>
  useQuery({
    queryKey: [QUERY_KEYS.FILTERS],
    queryFn: () => filtersApi.fetch(),
    select: (response) => response.data,
    staleTime: 600_000,
  })
