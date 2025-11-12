import { apiClient, API_ENDPOINTS } from '@/services/api'
import {
  buildPaginationQuery,
  buildQueryParams,
  buildFormData,
  buildBulkFormData,
  extractData,
  extractPaginatedResponse,
  extractItems,
  downloadExcel,
} from '@/utils/api'

// Types
export interface Material {
  id: number
  kode_barang: string | null
  nama_barang: string
  satuan: string
  kategori?: string
  harga?: number | null
  is_active: number
  created_at: string
  updated_at: string
}

export interface Mandor {
  id: number
  nama: string
  nomor_kontak?: string
  alamat?: string
  is_active: number
  created_at: string
  updated_at: string
}

export interface StockIn {
  id: number
  nomor_invoice: string
  material_id: number
  material?: Material
  quantity: number
  tanggal_masuk: string
  evidence_paths?: string
  surat_jalan_paths?: string
  material_datang_paths?: string
  created_at: string
  updated_at: string
}

export interface StockOut {
  id: number
  nomor_barang_keluar: string
  mandor_id: number
  mandor?: Mandor
  material_id: number
  material?: Material
  quantity: number
  quantity_terpasang?: number  // Total quantity yang sudah terpasang
  quantity_sisa_total?: number  // Sisa total (Qty Keluar - Terpasang) - untuk informasi
  quantity_sisa_kembali?: number  // Sisa bisa kembali (Qty Keluar - Terpasang - Sudah Kembali) - untuk validasi
  quantity_sudah_kembali?: number  // Total quantity yang sudah dikembalikan
  quantity_reject?: number  // Total quantity reject (informasi terpisah)
  quantity_sisa?: number  // Sisa quantity yang bisa dikembalikan (backward compatibility)
  tanggal_keluar: string
  evidence_paths?: string
  surat_permohonan_paths?: string
  surat_serah_terima_paths?: string
  created_at: string
  updated_at: string
}

export interface Installed {
  id: number
  material_id: number
  material?: Material
  quantity: number
  tanggal_pasang: string
  mandor_id: number
  mandor?: Mandor
  stock_out_id?: number
  stock_out?: StockOutBasic
  evidence_paths?: string
  no_register?: string
  created_at: string
  updated_at: string
}

export interface StockOutBasic {
  id: number
  nomor_barang_keluar: string
}

export interface Return {
  id: number
  mandor_id: number
  mandor?: Mandor
  material_id: number
  material?: Material
  quantity_kembali: number
  quantity_kondisi_baik?: number
  quantity_kondisi_reject?: number
  stock_out_id?: number
  stock_out?: StockOutBasic
  // Opsional: nomor barang keluar bisa diberikan langsung oleh API meski belum released
  nomor_barang_keluar?: string
  tanggal_kembali: string
  evidence_paths?: string
  is_released?: number
  created_at: string
  updated_at: string
}

export interface StockBalance {
  material_id: number
  kode_barang: string
  nama_barang: string
  satuan: string
  total_masuk: number
  total_keluar: number
  total_terpasang: number
  total_kembali: number
  total_retur_keluar?: number
  total_kondisi_baik?: number
  total_kondisi_reject?: number
  stock_ready?: number
  stock_saat_ini: number
}

export interface Discrepancy {
  mandor_id: number
  mandor_nama: string
  material_id: number
  material_kode: string
  material_nama: string
  barang_keluar: number
  barang_terpasang: number
  barang_kembali_dicatat: number
  selisih_seharusnya: number
  selisih_aktual: number
  status: string
}

export interface Notification {
  id: number
  mandor_id: number
  mandor_nama?: string
  material_id: number
  material_nama?: string
  title: string
  message: string
  barang_keluar: number
  barang_terpasang: number
  selisih: number
  status: string
  is_read: boolean
  created_at: string
  updated_at: string
}

// Request types
export interface MaterialCreateRequest {
  kode_barang?: string
  nama_barang: string
  satuan: string
  kategori?: string
  harga?: number | null
}

export interface MandorCreateRequest {
  nama: string
  nomor_kontak?: string
  alamat?: string
}

export interface StockInCreateRequest {
  nomor_invoice: string
  material_id: number
  quantity: number
  tanggal_masuk: string
}

export interface StockInBulkCreateRequest {
  nomor_invoice: string
  tanggal_masuk: string
  items: Array<{ material_id: number; quantity: number }>
}

export interface StockOutCreateRequest {
  mandor_id: number
  material_id: number
  quantity: number
  tanggal_keluar: string
}

export interface StockOutBulkCreateRequest {
  mandor_id: number
  tanggal_keluar: string
  items: Array<{ material_id: number; quantity: number }>
  nomor_surat_permintaan?: string
}

export interface InstalledCreateRequest {
  material_id: number
  quantity: number
  tanggal_pasang: string
  mandor_id: number
  stock_out_id?: number
  no_register?: string
}

export interface ReturnCreateRequest {
  mandor_id: number
  material_id: number
  quantity_kembali: number
  quantity_kondisi_baik?: number
  quantity_kondisi_reject?: number
  nomor_barang_keluar: string  // Wajib diisi - menggunakan nomor barang keluar (string)
  tanggal_kembali: string
}

export interface ExportExcelRequest {
  start_date?: string
  end_date?: string
  mandor_id?: number
  material_id?: number
}

export type ExportExcelRequestExt = ExportExcelRequest & { search?: string }

export interface SuratPermintaanItem {
  id?: number
  material_id?: number | null
  material?: Material
  kode_barang?: string | null
  nama_barang: string
  qty: number
  satuan: string
  sumber_barang?: {
    proyek?: boolean
    proyekValue?: string
    stok?: boolean
    stokValue?: string
  } | null
  peruntukan?: {
    proyek?: boolean
    proyekValue?: string
    produksi?: boolean
    produksiValue?: string
    kantor?: boolean
    lainLain?: boolean
  } | null
}

export interface SuratPermintaan {
  id: number
  nomor_surat: string
  tanggal: string
  project_id: number
  status?: string  // Draft, Barang Keluar Dibuat, Selesai
  project?: {
    id: number
    name: string
    code?: string | null
  }
  signatures?: {
    pemohon?: string
    menyetujui?: string
    yangMenyerahkan?: string
    mengetahuiSPV?: string
    mengetahuiAdminGudang?: string
  } | null
  items: SuratPermintaanItem[]
  created_by: number
  creator?: {
    id: number
    name: string
    email: string
  }
  created_at: string
  updated_at: string
}

export interface SuratPermintaanCreateRequest {
  tanggal: string
  items: Array<{
    material_id?: number | null
    kode_barang?: string | null
    nama_barang: string
    qty: number
    satuan: string
    sumber_barang?: {
      proyek?: boolean
      proyekValue?: string
      stok?: boolean
      stokValue?: string
    } | null
    peruntukan?: {
      proyek?: boolean
      proyekValue?: string
      produksi?: boolean
      produksiValue?: string
      kantor?: boolean
      lainLain?: boolean
    } | null
  }>
  signatures?: {
    pemohon?: string
    menyetujui?: string
    yangMenyerahkan?: string
    mengetahuiSPV?: string
    mengetahuiAdminGudang?: string
  } | null
}

// Surat Jalan Types
export interface SuratJalanItem {
  id?: number
  nama_barang: string
  qty: number
  keterangan?: string
}

export interface SuratJalan {
  id: number
  nomor_form: string
  kepada: string
  tanggal_pengiriman: string
  nama_pemberi?: string
  nama_penerima?: string
  tanggal_diterima?: string
  nomor_surat_permintaan?: string  // Relasi ke surat permintaan
  nomor_barang_keluar?: string  // Nomor barang keluar yang digunakan
  stock_out_id?: number  // Foreign key ke stock_out
  project_id: number
  created_by: number
  created_at: string
  updated_at: string
  items: SuratJalanItem[]
  project?: {
    id: number
    name: string
    code?: string
  }
  creator?: {
    id: number
    name: string
    email: string
  }
}

export interface SuratJalanCreateRequest {
  kepada: string
  tanggal_pengiriman: string
  items: SuratJalanItem[]
  nama_pemberi?: string
  nama_penerima?: string
  tanggal_diterima?: string
  nomor_surat_permintaan?: string  // Relasi ke surat permintaan
  nomor_barang_keluar?: string  // Nomor barang keluar yang akan digunakan sebagai nomor_form
}

export interface SuratJalanUpdateRequest {
  kepada?: string
  tanggal_pengiriman?: string
  items?: SuratJalanItem[]
  nama_pemberi?: string
  nama_penerima?: string
  tanggal_diterima?: string
}

// Helper: parse evidence_paths (JSON array string atau CSV) -> string[]
export function parseEvidencePaths(value?: string): string[] {
  if (!value) return []
  try {
    const parsed = JSON.parse(value)
    if (Array.isArray(parsed)) return parsed.filter(Boolean)
  } catch (_) {
    // fallback CSV
    return value.split(',').map((v) => v.trim()).filter(Boolean)
  }
  return []
}

// API Functions
export const inventoryService = {
  // Materials
  getMaterials: async (page = 1, limit = 100, search?: string) => {
    const query = buildPaginationQuery(page, limit, { search })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.MATERIALS.GET_ALL}${query}`)
    return extractData(response)
  },

  getMaterial: async (id: number) => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.MATERIALS.GET_BY_ID(id))
    return extractData(response)
  },

  getUniqueSatuans: async (): Promise<string[]> => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.MATERIALS.UNIQUE_SATUANS)
    return extractData<string[]>(response) || []
  },

  getUniqueKategoris: async (): Promise<string[]> => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.MATERIALS.UNIQUE_KATEGORIS)
    return extractData<string[]>(response) || []
  },

  createMaterial: async (data: MaterialCreateRequest) => {
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.MATERIALS.CREATE, data)
    return extractData(response)
  },

  updateMaterial: async (id: number, data: Partial<MaterialCreateRequest>) => {
    const response = await apiClient.put(API_ENDPOINTS.INVENTORY.MATERIALS.UPDATE(id), data)
    return extractData(response)
  },

  deleteMaterial: async (id: number) => {
    const response = await apiClient.delete(API_ENDPOINTS.INVENTORY.MATERIALS.DELETE(id))
    return extractData(response)
  },

  bulkImportMaterials: async (file: File) => {
    const formData = buildFormData({ file })
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.MATERIALS.BULK_IMPORT, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return extractData(response)
  },

  downloadMaterialTemplate: async () => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.MATERIALS.TEMPLATE, {
      responseType: 'blob',
    })
    
    const filename = `template_import_material_${new Date().toISOString().split('T')[0]}.xlsx`
    downloadExcel(response.data, filename)
    
    return response.data
  },

  // Mandors
  getMandors: async (page = 1, limit = 100, search?: string) => {
    const query = buildPaginationQuery(page, limit, { search })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.MANDORS.GET_ALL}${query}`)
    // Backend mengembalikan paginated_response, jadi gunakan extractPaginatedResponse
    return extractPaginatedResponse<Mandor>(response)
  },

  createMandor: async (data: MandorCreateRequest) => {
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.MANDORS.CREATE, data)
    return extractData(response)
  },

  updateMandor: async (id: number, data: Partial<MandorCreateRequest>) => {
    const response = await apiClient.put(API_ENDPOINTS.INVENTORY.MANDORS.UPDATE(id), data)
    return extractData(response)
  },

  // Stock In
  getStockIns: async (page = 1, limit = 10, search?: string, startDate?: string, endDate?: string) => {
    const query = buildPaginationQuery(page, limit, { search, start_date: startDate, end_date: endDate })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.STOCK_IN.GET_ALL}${query}`)
    return extractData(response)
  },

  createStockIn: async (data: StockInCreateRequest, files: File[]) => {
    const formData = buildFormData(
      {
        nomor_invoice: data.nomor_invoice,
        material_id: data.material_id,
        quantity: data.quantity,
        tanggal_masuk: data.tanggal_masuk,
      },
      { evidence: files }
    )
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.STOCK_IN.CREATE, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return extractData(response)
  },

  createStockInBulk: async (
    data: StockInBulkCreateRequest,
    evidenceFiles: File[] = [],
    suratJalanFiles: File[] = [],
    materialDatangFiles: File[] = []
  ) => {
    // Validate items before processing
    data.items.forEach((item, index) => {
      if (!Number.isInteger(item.quantity) || item.quantity <= 0) {
        throw new Error(`Quantity tidak valid pada item ke-${index + 1}`)
      }
    })

    const formData = buildBulkFormData(
      {
        nomor_invoice: data.nomor_invoice,
        tanggal_masuk: data.tanggal_masuk,
      },
      data.items,
      {
        evidence: evidenceFiles,
        surat_jalan: suratJalanFiles,
        material_datang: materialDatangFiles,
      }
    )

    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.STOCK_IN.CREATE_BULK, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return extractData(response)
  },

  updateStockIn: async (
    id: number,
    data: {
      nomor_invoice?: string
      material_id?: number
      quantity?: number
      tanggal_masuk?: string
    },
    evidenceFiles: File[] = [],
    suratJalanFiles: File[] = [],
    materialDatangFiles: File[] = []
  ) => {
    const formData = new FormData()
    
    if (data.nomor_invoice !== undefined) {
      formData.append('nomor_invoice', data.nomor_invoice)
    }
    if (data.material_id !== undefined) {
      formData.append('material_id', data.material_id.toString())
    }
    if (data.quantity !== undefined) {
      formData.append('quantity', data.quantity.toString())
    }
    if (data.tanggal_masuk !== undefined) {
      formData.append('tanggal_masuk', data.tanggal_masuk)
    }
    
    // Append files
    evidenceFiles.forEach((file) => {
      formData.append('evidence', file)
    })
    suratJalanFiles.forEach((file) => {
      formData.append('surat_jalan', file)
    })
    materialDatangFiles.forEach((file) => {
      formData.append('material_datang', file)
    })

    const response = await apiClient.put(API_ENDPOINTS.INVENTORY.STOCK_IN.UPDATE(id), formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return extractData(response)
  },

  // Stock Out
  getStockOuts: async (page = 1, limit = 10, search?: string, startDate?: string, endDate?: string) => {
    const query = buildPaginationQuery(page, limit, { search, start_date: startDate, end_date: endDate })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.STOCK_OUT.GET_ALL}${query}`)
    return extractData(response)
  },

  getStockOutsByMandor: async (mandorId: number) => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.STOCK_OUT.GET_BY_MANDOR(mandorId))
    return extractData(response)
  },

  getStockOutByNomor: async (nomor: string) => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.STOCK_OUT.GET_BY_NOMOR(nomor))
    return extractData(response)
  },

  getUniqueStockOutNumbers: async () => {
    // Mengambil semua stock out dengan pagination untuk mendapatkan unique nomor
    const allItems: StockOut[] = []
    let page = 1
    const limit = 1000 // Maksimum limit yang diizinkan
    let hasMore = true

    while (hasMore) {
      const query = buildPaginationQuery(page, limit, {})
      const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.STOCK_OUT.GET_ALL}${query}`)
      const data = extractData(response)
      const items = extractItems<StockOut>(data)
      
      if (items.length === 0) {
        hasMore = false
      } else {
        allItems.push(...items)
        // Jika jumlah items kurang dari limit, berarti sudah di halaman terakhir
        if (items.length < limit) {
          hasMore = false
        } else {
          page++
        }
      }
    }

    // Extract unique nomor_barang_keluar
    const uniqueNumbers = Array.from(new Set(allItems.map(item => item.nomor_barang_keluar)))
    return uniqueNumbers.sort().reverse() // Sort descending untuk menampilkan yang terbaru di atas
  },

  createStockOut: async (
    data: StockOutCreateRequest,
    evidenceFiles: File[] = [],
    suratPermohonanFiles: File[] = [],
    suratSerahTerimaFiles: File[] = []
  ) => {
    const formData = buildFormData(
      {
        mandor_id: data.mandor_id,
        material_id: data.material_id,
        quantity: data.quantity,
        tanggal_keluar: data.tanggal_keluar,
      },
      {
        evidence: evidenceFiles,
        surat_permohonan: suratPermohonanFiles,
        surat_serah_terima: suratSerahTerimaFiles,
      }
    )
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.STOCK_OUT.CREATE, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return extractData(response)
  },

  createStockOutBulk: async (
    data: StockOutBulkCreateRequest,
    evidenceFiles: File[] = [],
    suratPermohonanFiles: File[] = [],
    suratSerahTerimaFiles: File[] = []
  ) => {
    const baseFields: Record<string, string | number | boolean> = {
      mandor_id: data.mandor_id,
      tanggal_keluar: data.tanggal_keluar,
    }
    
    // Tambahkan nomor_surat_permintaan jika ada
    if (data.nomor_surat_permintaan) {
      baseFields.nomor_surat_permintaan = data.nomor_surat_permintaan
    }
    
    const formData = buildBulkFormData(
      baseFields,
      data.items,
      {
        evidence: evidenceFiles,
        surat_permohonan: suratPermohonanFiles,
        surat_serah_terima: suratSerahTerimaFiles,
      }
    )
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.STOCK_OUT.CREATE_BULK, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return extractData(response)
  },

  // Installed
  getInstalled: async (page = 1, limit = 10, search?: string, startDate?: string, endDate?: string) => {
    const query = buildPaginationQuery(page, limit, { search, start_date: startDate, end_date: endDate })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.INSTALLED.GET_ALL}${query}`)
    return extractData(response)
  },

  createInstalled: async (data: InstalledCreateRequest, files: File[] = []) => {
    const formDataFields: Record<string, string | number> = {
      material_id: data.material_id,
      quantity: data.quantity,
      tanggal_pasang: data.tanggal_pasang,
      mandor_id: data.mandor_id,
    }
    
    if (data.stock_out_id) {
      formDataFields.stock_out_id = data.stock_out_id
    }
    if (data.no_register) {
      formDataFields.no_register = data.no_register
    }

    const formData = buildFormData(formDataFields, { evidence: files })
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.INSTALLED.CREATE, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return extractData(response)
  },

  getInstalledByStockOutId: async (stockOutId: number) => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.INSTALLED.GET_BY_STOCK_OUT(stockOutId))
    return extractData(response)
  },

  // Return
  getReturns: async (params: {
    page?: number
    limit?: number
    is_released?: boolean
    mandor_id?: number
    material_id?: number
    search?: string
    start_date?: string
    end_date?: string
  }) => {
    const query = buildQueryParams(params)
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.RETURNS.GET_ALL}${query}`)
    return extractData(response)
  },

  getReturn: async (id: number) => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.RETURNS.GET_BY_ID(id))
    return extractData(response)
  },

  createReturn: async (data: ReturnCreateRequest, files: File[] = []) => {
    const formDataFields: Record<string, string | number> = {
      mandor_id: data.mandor_id,
      material_id: data.material_id,
      quantity_kembali: data.quantity_kembali,
      tanggal_kembali: data.tanggal_kembali,
      nomor_barang_keluar: data.nomor_barang_keluar,
    }

    if (data.quantity_kondisi_baik !== undefined && data.quantity_kondisi_baik !== null) {
      formDataFields.quantity_kondisi_baik = data.quantity_kondisi_baik
    }
    if (data.quantity_kondisi_reject !== undefined && data.quantity_kondisi_reject !== null) {
      formDataFields.quantity_kondisi_reject = data.quantity_kondisi_reject
    }

    const formData = buildFormData(formDataFields, { evidence: files })
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.RETURNS.CREATE, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return extractData(response)
  },

  releaseReturn: async (returnId: number, tanggal_keluar: string, files: File[] = []) => {
    const formData = buildFormData({ tanggal_keluar }, { evidence: files })
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.RETURNS.RELEASE(returnId), formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return extractData(response)
  },

  // Stock Balance
  getStockBalance: async (materialId?: number, search?: string, startDate?: string, endDate?: string) => {
    const query = buildQueryParams({ material_id: materialId, search, start_date: startDate, end_date: endDate })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.STOCK_BALANCE.GET_ALL}${query}`)
    return extractData(response)
  },

  // Discrepancy
  checkDiscrepancy: async () => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.DISCREPANCY.CHECK)
    return extractData(response)
  },

  // Notifications
  getNotifications: async (page = 1, limit = 100, isRead?: boolean) => {
    const query = buildPaginationQuery(page, limit, { is_read: isRead })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.NOTIFICATIONS.GET_ALL}${query}`)
    return extractData(response)
  },

  markNotificationRead: async (id: number) => {
    const response = await apiClient.patch(API_ENDPOINTS.INVENTORY.NOTIFICATIONS.MARK_READ(id))
    return extractData(response)
  },

  // Export Excel
  exportExcel: async (data: ExportExcelRequestExt) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.INVENTORY.EXPORT_EXCEL, data, {
        responseType: 'blob',
        validateStatus: (status) => status < 500,
      })
      
      // Check if response is an error (status >= 400)
      if (response.status >= 400) {
        if (response.data instanceof Blob) {
          const text = await response.data.text()
          try {
            const errorData = JSON.parse(text)
            throw new Error(errorData.detail || errorData.message || `Gagal export Excel (${response.status})`)
          } catch {
            throw new Error(`Gagal export Excel: ${text || `Status ${response.status}`}`)
          }
        }
        throw new Error(`Gagal export Excel: Status ${response.status}`)
      }
      
      // Check content type to ensure it's Excel file
      const contentType = response.headers['content-type'] || ''
      if (!contentType.includes('spreadsheet') && !contentType.includes('excel')) {
        if (response.data instanceof Blob) {
          const text = await response.data.text()
          try {
            const errorData = JSON.parse(text)
            throw new Error(errorData.detail || errorData.message || 'Gagal export Excel')
          } catch {
            throw new Error(`Gagal export Excel: ${text || 'Response tidak valid'}`)
          }
        }
      }
      
      const filename = `laporan_inventory_${new Date().toISOString().split('T')[0]}.xlsx`
      downloadExcel(response.data, filename)
      
      return response.data
    } catch (error: any) {
      if (error instanceof Error) {
        throw error
      }
      if (error?.response) {
        const status = error.response.status
        const errorData = error.response.data
        if (errorData instanceof Blob) {
          try {
            const text = await errorData.text()
            const parsed = JSON.parse(text)
            throw new Error(parsed.detail || parsed.message || `Gagal export Excel (${status})`)
          } catch {
            throw new Error(`Gagal export Excel: Status ${status}`)
          }
        }
        throw new Error(errorData?.detail || errorData?.message || `Gagal export Excel (${status})`)
      }
      throw new Error(error?.message || 'Gagal export Excel: Terjadi kesalahan tidak dikenal')
    }
  },

  // Surat Permintaan
  getSuratPermintaans: async (page = 1, limit = 10, search?: string, startDate?: string, endDate?: string) => {
    const query = buildPaginationQuery(page, limit, { search, start_date: startDate, end_date: endDate })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.SURAT_PERMINTAAN.GET_ALL}${query}`)
    // Return response lengkap dengan meta untuk pagination
    return response?.data || response
  },

  getSuratPermintaan: async (id: number) => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.SURAT_PERMINTAAN.GET_BY_ID(id))
    return extractData(response)
  },

  getSuratPermintaanByNomor: async (nomor_surat: string) => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.SURAT_PERMINTAAN.GET_BY_NOMOR(nomor_surat))
    return extractData(response)
  },

  createSuratPermintaan: async (data: SuratPermintaanCreateRequest) => {
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.SURAT_PERMINTAAN.CREATE, data)
    return extractData(response)
  },

  // Surat Jalan
  getSuratJalans: async (page = 1, limit = 10, search?: string, startDate?: string, endDate?: string) => {
    const query = buildPaginationQuery(page, limit, { search, start_date: startDate, end_date: endDate })
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.SURAT_JALAN.GET_ALL}${query}`)
    // Return response lengkap dengan meta untuk pagination
    return response?.data || response
  },

  getSuratJalan: async (id: number) => {
    const response = await apiClient.get(API_ENDPOINTS.INVENTORY.SURAT_JALAN.GET_BY_ID(id))
    return extractData(response)
  },

  createSuratJalan: async (data: SuratJalanCreateRequest) => {
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.SURAT_JALAN.CREATE, data)
    return extractData(response)
  },

  updateSuratJalan: async (id: number, data: SuratJalanUpdateRequest) => {
    const response = await apiClient.put(API_ENDPOINTS.INVENTORY.SURAT_JALAN.UPDATE(id), data)
    return extractData(response)
  },

  deleteSuratJalan: async (id: number) => {
    const response = await apiClient.delete(API_ENDPOINTS.INVENTORY.SURAT_JALAN.DELETE(id))
    return extractData(response)
  },
}
