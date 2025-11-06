/**
 * Helper untuk build FormData dengan type safety
 */

export interface FormDataField {
  name: string
  value: string | number | boolean | File
}

/**
 * Build FormData dari object atau array of fields
 */
export const buildFormData = (
  fields: Record<string, string | number | boolean | File | File[]>,
  fileFields?: Record<string, File | File[]>
): FormData => {
  const formData = new FormData()

  // Add regular fields
  Object.entries(fields).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        // Handle array of files separately
        value.forEach((item) => {
          if (item instanceof File) {
            formData.append(key, item)
          }
        })
      } else if (value instanceof File) {
        formData.append(key, value)
      } else {
        formData.append(key, String(value))
      }
    }
  })

  // Add file fields (if provided separately)
  if (fileFields) {
    Object.entries(fileFields).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach((file) => {
            if (file instanceof File) {
              formData.append(key, file)
            }
          })
        } else if (value instanceof File) {
          formData.append(key, value)
        }
      }
    })
  }

  return formData
}

/**
 * Build FormData untuk bulk operations dengan items JSON
 */
export const buildBulkFormData = (
  baseFields: Record<string, string | number | boolean>,
  items: Array<Record<string, any>>,
  fileFields?: Record<string, File | File[]>
): FormData => {
  const formData = buildFormData(baseFields, fileFields)
  formData.append('items', JSON.stringify(items))
  return formData
}

