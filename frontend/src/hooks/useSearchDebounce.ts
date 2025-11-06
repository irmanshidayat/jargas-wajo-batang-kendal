import { useEffect, useRef } from 'react'
import useDebounce from './useDebounce'

interface UseSearchDebounceOptions {
  searchTerm: string
  currentPage: number
  delay?: number
  onSearch: () => void
}

/**
 * Custom hook untuk handle search dengan debounce dan auto reset page ke 1
 * Menggunakan useDebounce untuk konsistensi dan mengurangi redundancy
 */
export const useSearchDebounce = ({
  searchTerm,
  currentPage,
  delay = 500,
  onSearch,
}: UseSearchDebounceOptions) => {
  const onSearchRef = useRef(onSearch)
  
  // Update ref when onSearch changes
  useEffect(() => {
    onSearchRef.current = onSearch
  }, [onSearch])

  // Use useDebounce hook untuk debounce searchTerm
  const debouncedSearchTerm = useDebounce(searchTerm, delay)

  useEffect(() => {
    if (currentPage === 1) {
      onSearchRef.current()
    }
  }, [debouncedSearchTerm, currentPage])
}

