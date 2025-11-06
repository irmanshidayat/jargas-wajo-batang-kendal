import { StockOut } from '../services/inventoryService'

/**
 * Interface untuk informasi sisa barang kembali
 */
export interface StockOutSisaInfo {
  quantity_terpasang: number
  quantity_sisa_kembali: number
  quantity_sudah_kembali: number
}

/**
 * Hitung informasi sisa barang kembali berdasarkan stock out
 * Rumus: Sisa = Qty Keluar - Qty Terpasang
 * 
 * @param stockOut Stock out object dari API
 * @returns Object dengan quantity_terpasang, quantity_sisa_kembali, dan quantity_sudah_kembali
 */
export const computeStockOutSisa = (stockOut: StockOut): StockOutSisaInfo => {
  // Prioritaskan quantity_terpasang dari backend jika ada
  const quantity_terpasang = (stockOut as any).quantity_terpasang ?? 0
  
  // Prioritaskan quantity_sisa_kembali dari backend, fallback ke perhitungan manual
  let quantity_sisa_kembali: number
  if ((stockOut as any).quantity_sisa_kembali !== undefined) {
    quantity_sisa_kembali = (stockOut as any).quantity_sisa_kembali
  } else {
    // Fallback: hitung manual (Qty Keluar - Qty Terpasang)
    quantity_sisa_kembali = Math.max(0, (stockOut.quantity ?? 0) - quantity_terpasang)
  }
  
  // Quantity sudah kembali (informasi saja)
  const quantity_sudah_kembali = (stockOut as any).quantity_sudah_kembali ?? 0
  
  return {
    quantity_terpasang,
    quantity_sisa_kembali: Math.max(0, quantity_sisa_kembali), // Pastikan tidak negatif
    quantity_sudah_kembali: Math.max(0, quantity_sudah_kembali),
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
  
  return `${stockOut.nomor_barang_keluar} - ${materialName} (Qty: ${stockOut.quantity}, Sudah kembali: ${sisaInfo.quantity_sudah_kembali}, Sisa: ${sisaInfo.quantity_sisa_kembali})${isFull ? ' (Sudah penuh)' : ''}`
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
    quantity_sisa_kembali: sisaInfo.quantity_sisa_kembali,
    quantity_sudah_kembali: sisaInfo.quantity_sudah_kembali,
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

