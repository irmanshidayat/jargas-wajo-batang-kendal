import Swal from 'sweetalert2'

/**
 * Interface untuk item form yang memiliki material_id dan quantity
 */
export interface FormItem {
  material_id: string
  quantity: string
}

/**
 * Interface untuk item yang sudah di-sanitize
 */
export interface SanitizedItem {
  material_id: string
  quantity: string
}

/**
 * Interface untuk item yang sudah di-convert ke number
 * material_id tetap integer, quantity bisa decimal (float)
 */
export interface NumberItem {
  material_id: number
  quantity: number
}

/**
 * Sanitize items dengan trim dan filter yang kosong
 * @param items Array of items dengan material_id dan quantity sebagai string
 * @returns Array of sanitized items
 */
export const sanitizeItems = (items: FormItem[]): SanitizedItem[] => {
  return items
    .map((it) => ({
      material_id: it.material_id.trim(),
      quantity: it.quantity.trim(),
    }))
    .filter((it) => it.material_id !== '' && it.quantity !== '')
}

/**
 * Validasi quantity harus >= 0.01 dan bisa decimal
 * @param quantity String quantity yang akan divalidasi
 * @param rowIndex Index baris (1-based) untuk pesan error
 * @returns Object dengan isValid (boolean) dan errorMessage (string | null)
 */
export const validateQuantity = (
  quantity: string,
  rowIndex: number
): { isValid: boolean; errorMessage: string | null } => {
  const q = parseFloat(quantity)
  if (isNaN(q) || q < 0.01) {
    return {
      isValid: false,
      errorMessage: `Quantity pada baris ${rowIndex} harus bilangan desimal minimal 0.01`,
    }
  }
  return { isValid: true, errorMessage: null }
}

/**
 * Validasi semua quantity dalam items
 * @param sanitizedItems Array of sanitized items
 * @returns Object dengan isValid (boolean) dan errorMessage (string | null)
 */
export const validateAllQuantities = (
  sanitizedItems: SanitizedItem[]
): { isValid: boolean; errorMessage: string | null } => {
  for (let i = 0; i < sanitizedItems.length; i++) {
    const validation = validateQuantity(sanitizedItems[i].quantity, i + 1)
    if (!validation.isValid) {
      return validation
    }
  }
  return { isValid: true, errorMessage: null }
}

/**
 * Cek apakah ada duplikat material_id dalam items
 * @param sanitizedItems Array of sanitized items
 * @returns true jika ada duplikat, false jika tidak ada
 */
export const hasDuplicateMaterials = (
  sanitizedItems: SanitizedItem[]
): boolean => {
  const materialIds = sanitizedItems.map((it) => it.material_id)
  return new Set(materialIds).size !== materialIds.length
}

/**
 * Convert items dari string ke number (material_id dan quantity)
 * @param sanitizedItems Array of sanitized items
 * @returns Array of items dengan material_id sebagai integer dan quantity sebagai float
 */
export const convertItemsToNumbers = (
  sanitizedItems: SanitizedItem[]
): NumberItem[] => {
  return sanitizedItems.map((it, index) => {
    const materialId = parseInt(it.material_id, 10)
    const quantity = parseFloat(it.quantity)
    
    // DEBUG: Log conversion untuk tracking
    console.log(`[DEBUG convertItemsToNumbers] Item ${index + 1}:`, {
      original_material_id: it.material_id,
      converted_material_id: materialId,
      original_quantity: it.quantity,
      converted_quantity: quantity,
      quantity_type: typeof quantity,
      isNaN_quantity: isNaN(quantity),
    })
    
    // Validasi konversi tidak menghasilkan NaN
    if (isNaN(materialId) || isNaN(quantity)) {
      console.error(`[ERROR convertItemsToNumbers] NaN detected for item ${index + 1}:`, it)
      throw new Error(`Gagal mengkonversi material_id atau quantity pada baris ${index + 1}`)
    }
    
    return {
      material_id: materialId,
      quantity: quantity,
    }
  })
}

/**
 * Validasi dan tampilkan error dengan SweetAlert jika tidak valid
 * @param validation Result dari validateAllQuantities atau validateQuantity
 * @returns true jika valid, false jika tidak valid
 */
export const showValidationErrorIfInvalid = (
  validation: { isValid: boolean; errorMessage: string | null }
): boolean => {
  if (!validation.isValid && validation.errorMessage) {
    Swal.fire({
      icon: 'warning',
      title: 'Perhatian',
      text: validation.errorMessage,
    })
    return false
  }
  return true
}

/**
 * Validasi dan tampilkan error duplikat material dengan SweetAlert
 * @param hasDuplicate true jika ada duplikat
 * @returns true jika tidak ada duplikat, false jika ada duplikat
 */
export const showDuplicateErrorIfExists = (hasDuplicate: boolean): boolean => {
  if (hasDuplicate) {
    Swal.fire({
      icon: 'warning',
      title: 'Perhatian',
      text: 'Terdapat duplikat material. Mohon gabungkan/hapus duplikat.',
    })
    return false
  }
  return true
}

/**
 * Validasi items kosong dan tampilkan error jika kosong
 * @param sanitizedItems Array of sanitized items
 * @param errorMessage Pesan error yang akan ditampilkan (default: 'Minimal 1 baris material dan quantity harus diisi')
 * @returns true jika tidak kosong, false jika kosong
 */
export const validateItemsNotEmpty = (
  sanitizedItems: SanitizedItem[],
  errorMessage: string = 'Minimal 1 baris material dan quantity harus diisi'
): boolean => {
  if (sanitizedItems.length === 0) {
    Swal.fire({
      icon: 'warning',
      title: 'Perhatian',
      text: errorMessage,
    })
    return false
  }
  return true
}

/**
 * Helper untuk parse quantity string ke number dengan handling khusus untuk ReturnsPage
 * (mengembalikan { value, wasFilled } untuk membedakan antara empty dan value 0)
 * @param value String quantity
 * @returns Object dengan value (number) dan wasFilled (boolean)
 */
export const parseQuantityWithFlag = (value: string): { value: number; wasFilled: boolean } => {
  const trimmed = value.trim()
  
  // Empty string atau tidak ada nilai = tidak diisi
  if (trimmed === '') {
    return { value: 0, wasFilled: false }
  }
  
  // Jika ada nilai (termasuk "0"), anggap sebagai user input
  const parsed = parseFloat(trimmed)
  const result = isNaN(parsed) ? 0 : parsed
  return { value: result, wasFilled: true }
}

