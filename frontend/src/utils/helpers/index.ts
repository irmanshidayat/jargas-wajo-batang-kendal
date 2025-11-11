/**
 * Get today's date in YYYY-MM-DD format
 */
export const getTodayDate = (): string => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Format number to decimal string with 2 decimal places
 * @param value Number or string value to format
 * @returns Formatted string with 2 decimal places (e.g., "1.20", "1.00")
 */
export const formatDecimal = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') {
    return '-'
  }
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue)) {
    return '-'
  }
  return numValue.toFixed(2)
}

/**
 * Check if error is a canceled request error
 * @param error Error object to check
 * @returns true if error is a canceled request, false otherwise
 */
export const isCanceledError = (error: any): boolean => {
  if (!error) return false
  
  return (
    error.name === 'CanceledError' ||
    error.message === 'canceled' ||
    error.code === 'ERR_CANCELED' ||
    (error.message && typeof error.message === 'string' && error.message.toLowerCase().includes('canceled')) ||
    (error.config?.signal && error.config.signal.aborted)
  )
}