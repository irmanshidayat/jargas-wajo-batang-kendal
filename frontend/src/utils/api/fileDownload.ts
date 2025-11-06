/**
 * Helper untuk download file dari blob response
 */

/**
 * Download blob sebagai file dengan nama tertentu
 */
export const downloadBlob = (
  blob: Blob,
  filename: string,
  mimeType?: string
): void => {
  const blobWithType = mimeType
    ? new Blob([blob], { type: mimeType })
    : blob

  const url = window.URL.createObjectURL(blobWithType)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

/**
 * Download Excel file dari blob response
 */
export const downloadExcel = (blob: Blob, filename: string): void => {
  downloadBlob(
    blob,
    filename,
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  )
}

