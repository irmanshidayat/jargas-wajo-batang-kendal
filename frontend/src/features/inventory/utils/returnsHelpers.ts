import { StockOut } from '../services/inventoryService'
import { formatDecimalOne } from '@/utils/helpers'

/**
 * Interface untuk informasi sisa barang kembali
 * BEST PRACTICE: Struktur yang jelas dan konsisten
 */
export interface StockOutSisaInfo {
  quantity_terpasang: number  // Total yang sudah terpasang
  quantity_sisa_total: number  // Sisa total (Qty - Terpasang) - untuk informasi
  quantity_sisa_kembali: number  // Sisa bisa kembali (Qty - Terpasang - Sudah Kembali) - untuk validasi
  quantity_sudah_kembali: number  // Total yang sudah dikembalikan
  quantity_reject?: number  // Total reject (opsional, untuk informasi)
}

/**
 * Hitung informasi sisa barang kembali berdasarkan stock out
 * BEST PRACTICE: Menggunakan data dari backend jika tersedia, fallback ke perhitungan manual
 * 
 * @param stockOut Stock out object dari API
 * @returns Object dengan informasi sisa yang lengkap
 */
export const computeStockOutSisa = (stockOut: StockOut): StockOutSisaInfo => {
  // Prioritaskan data dari backend jika ada
  const quantity_terpasang = stockOut.quantity_terpasang ?? 0
  const quantity_sudah_kembali = stockOut.quantity_sudah_kembali ?? 0
  const quantity_reject = stockOut.quantity_reject
  
  // BEST PRACTICE: Gunakan quantity_sisa_total dari backend jika ada
  let quantity_sisa_total: number
  if (stockOut.quantity_sisa_total !== undefined) {
    quantity_sisa_total = stockOut.quantity_sisa_total
  } else {
    // Fallback: hitung manual (Qty Keluar - Qty Terpasang)
    quantity_sisa_total = Math.max(0, (stockOut.quantity ?? 0) - quantity_terpasang)
  }
  
  // BEST PRACTICE: Gunakan quantity_sisa_kembali dari backend jika ada
  let quantity_sisa_kembali: number
  if (stockOut.quantity_sisa_kembali !== undefined) {
    quantity_sisa_kembali = stockOut.quantity_sisa_kembali
  } else {
    // Fallback: hitung manual (Qty Keluar - Qty Terpasang - Sudah Kembali)
    quantity_sisa_kembali = Math.max(0, (stockOut.quantity ?? 0) - quantity_terpasang - quantity_sudah_kembali)
  }
  
  return {
    quantity_terpasang: Math.max(0, quantity_terpasang),
    quantity_sisa_total: Math.max(0, quantity_sisa_total),
    quantity_sisa_kembali: Math.max(0, quantity_sisa_kembali),
    quantity_sudah_kembali: Math.max(0, quantity_sudah_kembali),
    ...(quantity_reject !== undefined && { quantity_reject: Math.max(0, quantity_reject) }),
  }
}

/**
 * Format label untuk dropdown option stock out
 * 
 * @param stockOut Stock out object
 * @returns Formatted string untuk dropdown option
 */
export const formatStockOutOptionLabel = (stockOut: StockOut): string => {
  const sisaInfo = computeStockOutSisa(stockOut)
  const materialName = stockOut.material?.nama_barang || `Material ID: ${stockOut.material_id}`
  const isFull = sisaInfo.quantity_sisa_kembali <= 0
  
  return `${stockOut.nomor_barang_keluar} - ${materialName} (Qty: ${formatDecimalOne(stockOut.quantity)}, Terpasang: ${formatDecimalOne(sisaInfo.quantity_terpasang)}, Sisa: ${formatDecimalOne(sisaInfo.quantity_sisa_total)}, Sudah kembali: ${formatDecimalOne(sisaInfo.quantity_sudah_kembali)}, Bisa kembali: ${formatDecimalOne(sisaInfo.quantity_sisa_kembali)})${isFull ? ' (Sudah penuh)' : ''}`
}

/**
 * Format info card untuk stock out yang dipilih
 * 
 * @param stockOut Stock out object
 * @returns Formatted JSX atau null
 */
export const formatStockOutInfoCard = (stockOut: StockOut) => {
  const sisaInfo = computeStockOutSisa(stockOut)
  const materialName = stockOut.material?.nama_barang || `ID: ${stockOut.material_id}`
  
  return {
    materialName,
    quantity: stockOut.quantity,
    quantity_terpasang: sisaInfo.quantity_terpasang,
    quantity_sisa_total: sisaInfo.quantity_sisa_total,  // Sisa total (Qty - Terpasang)
    quantity_sisa_kembali: sisaInfo.quantity_sisa_kembali,  // Sisa bisa kembali (untuk validasi)
    quantity_sudah_kembali: sisaInfo.quantity_sudah_kembali,
    quantity_reject: sisaInfo.quantity_reject,
  }
}

/**
 * Cek apakah stock out sudah penuh (sisa <= 0)
 * 
 * @param stockOut Stock out object
 * @returns true jika sudah penuh, false jika masih ada sisa
 */
export const isStockOutFull = (stockOut: StockOut): boolean => {
  const sisaInfo = computeStockOutSisa(stockOut)
  return sisaInfo.quantity_sisa_kembali <= 0
}

/**
 * Get placeholder text untuk dropdown stock out
 * 
 * @param params Object dengan kondisi dropdown
 * @returns Placeholder text
 */
export const getStockOutDropdownPlaceholder = (params: {
  loading: boolean
  hasMandor: boolean
  hasItems: boolean
  isRequired?: boolean
}): string => {
  const { loading, hasMandor, hasItems, isRequired = false } = params
  
  if (loading) return 'Memuat data...'
  if (!hasMandor) return 'Pilih Mandor terlebih dahulu'
  if (!hasItems) return 'Tidak ada data barang keluar untuk mandor ini'
  return isRequired ? 'Pilih Nomor Barang Keluar' : 'Pilih Nomor Barang Keluar (opsional)'
}

