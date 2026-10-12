import { keepPreviousData, useQuery } from '@tanstack/react-query'
import noticesApi from 'apis/notices'
import { QUERY_KEYS } from 'constants/query'
import { isPresent } from 'utils'

export const useFetchNotices = (params) =>
  useQuery({
    queryKey: [QUERY_KEYS.NOTICES, params],
    queryFn: () => noticesApi.fetch(params),
    select: (response) => response.data,
    placeholderData: keepPreviousData,
  })

export const useShowNotice = (id) =>
  useQuery({
    queryKey: [QUERY_KEYS.NOTICE, id],
    queryFn: () => noticesApi.show(id),
    select: (response) => response.data,
    enabled: isPresent(id),
  })
