/**
 * Helper untuk build query parameters dengan type safety
 */
export interface QueryParams {
  page?: number
  limit?: number
  search?: string
  start_date?: string
  end_date?: string
  is_released?: boolean
  is_read?: boolean
  is_active?: boolean
  mandor_id?: number
  material_id?: number
  page_id?: number
  include_permissions?: boolean
  [key: string]: string | number | boolean | undefined
}

/**
 * Build query string dari object parameters
 * Menghilangkan undefined/null values
 */
export const buildQueryParams = (params: QueryParams): string => {
  const searchParams = new URLSearchParams()
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value))
    }
  })
  
  const queryString = searchParams.toString()
  return queryString ? `?${queryString}` : ''
}

/**
 * Build query string dengan default pagination
 */
export const buildPaginationQuery = (
  page: number = 1,
  limit: number = 100,
  additionalParams?: Partial<QueryParams>
): string => {
  return buildQueryParams({
    page,
    limit,
    ...additionalParams,
  })
}

