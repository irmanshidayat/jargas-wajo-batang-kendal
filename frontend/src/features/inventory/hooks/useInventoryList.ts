import { useCallback, useEffect, useMemo, useState, useRef } from 'react'
import Swal from 'sweetalert2'

interface UseInventoryListOptions<T> {
  fetchFunction: (params: {
    page: number
    limit: number
    search?: string
    startDate?: string
    endDate?: string
  }) => Promise<any>
  extractItems: (response: any) => T[]
  defaultLimit?: number
  enableAutoRefresh?: boolean
  autoRefreshInterval?: number
  errorMessage?: string
}

export function useInventoryList<T>({
  fetchFunction,
  extractItems,
  defaultLimit = 10,
  enableAutoRefresh = false,
  autoRefreshInterval = 600000, // 10 menit default
  errorMessage = 'Gagal memuat data',
}: UseInventoryListOptions<T>) {
  const [data, setData] = useState<T[]>([])
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [limit] = useState(defaultLimit)
  const [total, setTotal] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(total / limit))
  }, [total, limit])

  // Store latest values in refs untuk menghindari dependency issues
  const fetchFunctionRef = useRef(fetchFunction)
  const extractItemsRef = useRef(extractItems)
  const errorMessageRef = useRef(errorMessage)
  const stateRef = useRef({ page, limit, searchTerm, startDate, endDate })
  
  useEffect(() => {
    fetchFunctionRef.current = fetchFunction
    extractItemsRef.current = extractItems
    errorMessageRef.current = errorMessage
    stateRef.current = { page, limit, searchTerm, startDate, endDate }
  }, [fetchFunction, extractItems, errorMessage, page, limit, searchTerm, startDate, endDate])

  const fetchData = useCallback(
    async (options?: { showLoader?: boolean }) => {
      const showLoader = options?.showLoader ?? true
      try {
        setLoading(true)
        if (showLoader) {
          Swal.fire({
            title: 'Memuat...',
            allowOutsideClick: false,
            didOpen: () => {
              Swal.showLoading()
            },
          })
        }
        const response = await fetchFunctionRef.current({
          page,
          limit,
          search: searchTerm || undefined,
          startDate: startDate || undefined,
          endDate: endDate || undefined,
        })
        const items = extractItemsRef.current(response)
        setData(items)
        const responseTotal =
          response?.meta?.pagination?.total || response?.total || items.length
        setTotal(responseTotal)
      } catch (error: any) {
        // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
        if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
          return
        }
        
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error?.response?.data?.detail || errorMessageRef.current,
        })
      } finally {
        if (Swal.isVisible()) Swal.close()
        setLoading(false)
      }
    },
    [page, limit, searchTerm, startDate, endDate]
  )

  // Fetch saat parameter berubah (debounced) - hanya saat parameter berubah
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      // Fetch langsung tanpa bergantung pada fetchData callback
      const performFetch = async () => {
        try {
          setLoading(true)
          Swal.fire({
            title: 'Memuat...',
            allowOutsideClick: false,
            didOpen: () => {
              Swal.showLoading()
            },
          })
          const response = await fetchFunctionRef.current({
            page,
            limit,
            search: searchTerm || undefined,
            startDate: startDate || undefined,
            endDate: endDate || undefined,
          })
          const items = extractItemsRef.current(response)
          setData(items)
          const responseTotal =
            response?.meta?.pagination?.total || response?.total || items.length
          setTotal(responseTotal)
        } catch (error: any) {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error?.response?.data?.detail || errorMessageRef.current,
          })
        } finally {
          if (Swal.isVisible()) Swal.close()
          setLoading(false)
        }
      }
      performFetch()
    }, 500)
    return () => clearTimeout(debounceTimer)
  }, [page, limit, searchTerm, startDate, endDate]) // Hanya trigger saat parameter berubah

  // Auto refresh berkala (opsional) - hanya bergantung pada enableAutoRefresh dan interval
  // Menggunakan ref untuk state terbaru tanpa restart interval
  useEffect(() => {
    if (!enableAutoRefresh) return
    
    const intervalId = setInterval(() => {
      // Fetch data langsung tanpa loader menggunakan state terbaru dari ref
      const performFetch = async () => {
        try {
          const currentState = stateRef.current
          setLoading(true)
          const response = await fetchFunctionRef.current({
            page: currentState.page,
            limit: currentState.limit,
            search: currentState.searchTerm || undefined,
            startDate: currentState.startDate || undefined,
            endDate: currentState.endDate || undefined,
          })
          const items = extractItemsRef.current(response)
          setData(items)
          const responseTotal =
            response?.meta?.pagination?.total || response?.total || items.length
          setTotal(responseTotal)
        } catch (error: any) {
          // Silent error untuk auto-refresh, tidak perlu show alert
          console.error('Auto-refresh error:', error)
        } finally {
          setLoading(false)
        }
      }
      performFetch()
    }, autoRefreshInterval)
    
    return () => clearInterval(intervalId)
  }, [enableAutoRefresh, autoRefreshInterval]) // Hanya restart jika enableAutoRefresh atau interval berubah

  const handlePageChange = (newPage: number) => {
    setPage(newPage)
  }

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    setPage(1) // Reset to first page when search changes
  }

  const handleDateChange = (start: string, end: string) => {
    setStartDate(start)
    setEndDate(end)
    setPage(1) // Reset to first page when filter changes
  }

  return {
    data,
    loading,
    page,
    limit,
    total,
    totalPages,
    searchTerm,
    startDate,
    endDate,
    setPage: handlePageChange,
    setSearchTerm: handleSearchChange,
    setStartDate: (start: string) => handleDateChange(start, endDate),
    setEndDate: (end: string) => handleDateChange(startDate, end),
    onDateChange: handleDateChange,
    fetchData,
  }
}

