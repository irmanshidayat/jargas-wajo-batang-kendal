/**
 * Helper untuk extract response data dengan konsisten
 * Backend response format: { success, message, data, meta?: { pagination } }
 */

export interface ApiResponse<T> {
  success?: boolean
  message?: string
  data: T
  meta?: {
    pagination?: {
      total: number
      page: number
      limit: number
    }
  }
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  message?: string
}

/**
 * Extract data dari API response
 * Backend response format melalui axios: { data: { success, message, data: [...], meta?: {...} } }
 */
export const extractData = <T>(response: any): T => {
  // Axios response structure: response.data adalah response body dari backend
  // Backend response structure: { success, message, data: [...], meta?: {...} }
  
  // Jika response.data ada dan memiliki property data, itu adalah struktur backend
  if (response?.data?.data !== undefined) {
    return response.data.data as T
  }
  
  // Jika response.data ada tapi tidak punya property data, mungkin response.data langsung isinya
  if (response?.data !== undefined) {
    // Jika response.data adalah array atau object langsung, return itu
    return response.data as T
  }
  
  // Fallback: return response langsung jika tidak ada struktur nested
  return response as T
}

/**
 * Extract paginated response dengan transformasi ke format konsisten
 */
export const extractPaginatedResponse = <T>(
  response: any
): PaginatedResponse<T> => {
  const backendData = response?.data || response
  
  return {
    data: (backendData?.data || backendData || []) as T[],
    total: backendData?.meta?.pagination?.total || 0,
    page: backendData?.meta?.pagination?.page || 1,
    limit: backendData?.meta?.pagination?.limit || 100,
    message: backendData?.message || 'Data berhasil diambil',
  }
}

/**
 * Extract items dari response (untuk backward compatibility)
 */
export const extractItems = <T = any>(response: any): T[] => {
  const data = response?.data ?? response
  if (Array.isArray(data?.items)) return data.items as T[]
  if (Array.isArray(data?.data)) return data.data as T[]
  if (Array.isArray(data)) return data as T[]
  if (Array.isArray(response?.items)) return response.items as T[]
  return []
}

