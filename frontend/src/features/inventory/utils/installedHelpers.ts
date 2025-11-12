import { StockOut } from '../services/inventoryService'
import { formatDecimalOne } from '@/utils/helpers'

export const getSisaPasang = (stockOut: Partial<StockOut> & Record<string, any>): number | undefined => {
  if (stockOut == null) return undefined
  if (stockOut.quantity_sisa_kembali !== undefined && stockOut.quantity_sisa_kembali !== null) {
    return Number(stockOut.quantity_sisa_kembali)
  }
  if ((stockOut as any).quantity_sisa !== undefined && (stockOut as any).quantity_sisa !== null) {
    return Number((stockOut as any).quantity_sisa)
  }
  return undefined
}

export const getInstalledMaxQty = (stockOut: Partial<StockOut> & Record<string, any>): number | undefined => {
  return getSisaPasang(stockOut)
}

export const formatInstalledStockOutOption = (stockOut: Partial<StockOut> & Record<string, any>): string => {
  const materialName = stockOut.material?.nama_barang || `Material ID: ${stockOut.material_id}`
  const mandorName = stockOut.mandor?.nama || `Mandor ID: ${stockOut.mandor_id}`
  const sisa = getSisaPasang(stockOut)
  return `${stockOut.nomor_barang_keluar} - ${materialName} (Mandor: ${mandorName}, Sisa: ${formatDecimalOne(sisa)})`
}


