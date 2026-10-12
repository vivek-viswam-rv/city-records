import { useEffect, useMemo, useState } from 'react'
import debounce from 'lodash/debounce'

const useDebouncedValue = (value, ms = 300) => {
  const [debounced, setDebounced] = useState(value)
  const update = useMemo(() => debounce(setDebounced, ms), [ms])

  useEffect(() => {
    update(value)
  }, [update, value])

  useEffect(() => () => update.cancel(), [update])

  return debounced
}

export default useDebouncedValue
