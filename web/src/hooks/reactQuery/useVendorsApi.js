import { useQuery } from '@tanstack/react-query'
import vendorsApi from 'apis/vendors'
import { QUERY_KEYS } from 'constants/query'

export const useShowVendor = (id) =>
  useQuery({
    queryKey: [QUERY_KEYS.VENDOR, id],
    queryFn: () => vendorsApi.show(id),
    select: (response) => response.data,
  })
