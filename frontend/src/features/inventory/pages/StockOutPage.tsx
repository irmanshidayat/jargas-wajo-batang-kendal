import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { inventoryService, Material, Mandor, SuratPermintaan } from '../services/inventoryService'
import EvidenceUpload from '../components/EvidenceUpload'
import Swal from 'sweetalert2'
import { getTodayDate, formatDecimal } from '@/utils/helpers'
import { extractItems } from '@/utils/api'
import {
  sanitizeItems,
  validateItemsNotEmpty,
  validateAllQuantities,
  hasDuplicateMaterials,
  showValidationErrorIfInvalid,
  showDuplicateErrorIfExists,
  convertItemsToNumbers,
} from '../utils/formValidation'

export default function StockOutPage() {
  const navigate = useNavigate()
  const [materials, setMaterials] = useState<Material[]>([])
  const [mandors, setMandors] = useState<Mandor[]>([])
  const [loading, setLoading] = useState(false)
  const [materialStocks, setMaterialStocks] = useState<{ [key: number]: number }>({})
  const [formData, setFormData] = useState({
    mandor_id: '',
    tanggal_keluar: getTodayDate(),
  })
  const [items, setItems] = useState<Array<{ material_id: string; quantity: string }>>([
    { material_id: '', quantity: '' },
  ])
  const [suratPermohonanFiles, setSuratPermohonanFiles] = useState<File[]>([])
  const [suratSerahTerimaFiles, setSuratSerahTerimaFiles] = useState<File[]>([])
  const [suratPermintaans, setSuratPermintaans] = useState<SuratPermintaan[]>([])
  const [selectedNomorSurat, setSelectedNomorSurat] = useState<string>('')
  const [loadingSuratPermintaan, setLoadingSuratPermintaan] = useState(false)
  const [isSuratPermintaanDropdownOpen, setIsSuratPermintaanDropdownOpen] = useState(false)
  const [searchSuratPermintaanTerm, setSearchSuratPermintaanTerm] = useState('')
  const suratPermintaanDropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadMaterials()
    loadMandors()
    loadSuratPermintaans()
  }, [])

  const loadMaterials = async () => {
    try {
      const response = await inventoryService.getMaterials(1, 1000)
      const items = Array.isArray(response?.data)
        ? response.data
        : Array.isArray(response)
          ? response
          : (response?.data?.items || response?.data || response?.items || [])
      setMaterials(items as Material[])
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Gagal memuat data materials',
      })
    }
  }

  const loadMandors = async () => {
    try {
      const response = await inventoryService.getMandors(1, 1000)
      setMandors(response.data || response.items || [])
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Gagal memuat data mandors',
      })
    }
  }

  const loadSuratPermintaans = async () => {
    try {
      const response = await inventoryService.getSuratPermintaans(1, 1000)
      const items = extractItems<SuratPermintaan>(response)
      setSuratPermintaans(items)
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Gagal memuat data surat permintaan',
      })
    }
  }

  const handleSelectNomorSurat = async (nomorSurat: string) => {
    if (!nomorSurat) {
      setSelectedNomorSurat('')
      setItems([{ material_id: '', quantity: '' }])
      return
    }

    try {
      setLoadingSuratPermintaan(true)
      const response = await inventoryService.getSuratPermintaanByNomor(nomorSurat)
      const suratPermintaan = response?.data || response

      if (suratPermintaan && suratPermintaan.items && suratPermintaan.items.length > 0) {
        // Auto-fill items dari surat permintaan
        const autoFilledItems = suratPermintaan.items.map((item: any) => {
          // Gunakan material_id jika ada, jika tidak maka kosongkan (user bisa isi manual)
          const materialId = item.material_id || item.material?.id || ''
          return {
            material_id: materialId ? materialId.toString() : '',
            quantity: item.qty ? item.qty.toString() : '',
          }
        })

        setItems(autoFilledItems.length > 0 ? autoFilledItems : [{ material_id: '', quantity: '' }])
        setSelectedNomorSurat(nomorSurat)
      } else {
        Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Surat permintaan tidak memiliki item',
        })
        setSelectedNomorSurat('')
      }
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || error.response?.data?.message || 'Gagal memuat detail surat permintaan',
      })
      setSelectedNomorSurat('')
    } finally {
      setLoadingSuratPermintaan(false)
    }
  }

  // Handle click outside untuk dropdown surat permintaan
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suratPermintaanDropdownRef.current && !suratPermintaanDropdownRef.current.contains(event.target as Node)) {
        setIsSuratPermintaanDropdownOpen(false)
        setSearchSuratPermintaanTerm('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  // Filter surat permintaan berdasarkan search term
  const filteredSuratPermintaans = suratPermintaans.filter((sp) =>
    sp.nomor_surat.toLowerCase().includes(searchSuratPermintaanTerm.toLowerCase())
  )

  // Ambil stok saat ini ketika material berubah di items
  useEffect(() => {
    const fetchStocks = async () => {
      const materialIds = items
        .map((item) => item.material_id)
        .filter((id) => id !== '')
        .map((id) => parseInt(id))
        .filter((id) => !isNaN(id))

      if (materialIds.length === 0) {
        setMaterialStocks({})
        return
      }

      const newStocks: { [key: number]: number } = {}
      
      // Fetch stock for each unique material
      const uniqueIds = Array.from(new Set(materialIds))
      
      for (const materialId of uniqueIds) {
        try {
          const res = await inventoryService.getStockBalance(materialId)
          const raw = (res?.data?.data ?? res?.data ?? res) as any
          let stockNow: number | null = null
          
          if (Array.isArray(raw)) {
            const item = raw.find((x: any) => x.material_id === materialId) || raw[0]
            // Gunakan stock_ready (sudah dikurangi reject) sebagai prioritas utama
            stockNow = item ? (item.stock_ready ?? item.stock_saat_ini ?? item.stock ?? null) : null
          } else if (raw && typeof raw === 'object') {
            // Gunakan stock_ready (sudah dikurangi reject) sebagai prioritas utama
            stockNow = raw.stock_ready ?? raw.stock_saat_ini ?? raw.stock ?? null
          }
          
          if (typeof stockNow === 'number') {
            newStocks[materialId] = stockNow
          }
        } catch (error: any) {
          console.error(`Failed to fetch stock for material ${materialId}:`, error)
        }
      }
      
      setMaterialStocks(newStocks)
    }
    
    fetchStocks()
  }, [items])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validasi dasar
    if (!formData.mandor_id || !formData.tanggal_keluar) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Mandor dan tanggal keluar wajib diisi',
      })
      return
    }

    // Validasi items
    const sanitized = sanitizeItems(items)
    
    if (!validateItemsNotEmpty(sanitized)) return
    
    // Validasi quantity
    const quantityValidation = validateAllQuantities(sanitized)
    if (!showValidationErrorIfInvalid(quantityValidation)) return
    
    // Cek duplikat material
    if (!showDuplicateErrorIfExists(hasDuplicateMaterials(sanitized))) return

    // Validasi stock untuk setiap item
    const numberItems = convertItemsToNumbers(sanitized)
    for (let i = 0; i < numberItems.length; i++) {
      const materialId = numberItems[i].material_id
      const quantity = numberItems[i].quantity
      const currentStock = materialStocks[materialId]
      
      if (currentStock === undefined || currentStock === null) {
        Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Stok untuk material pada baris ${i + 1} belum dimuat. Mohon tunggu atau refresh halaman.`,
        })
        return
      }

      if (currentStock <= 0) {
        const material = materials.find((m) => m.id === materialId)
        const materialName = material ? `${material.kode_barang} - ${material.nama_barang}` : `ID ${materialId}`
        Swal.fire({
          icon: 'warning',
          title: 'Stok Tidak Cukup',
          text: `Stok untuk material ${materialName} pada baris ${i + 1} adalah 0. Tidak dapat melanjutkan.`,
        })
        return
      }

      if (quantity > currentStock) {
        const material = materials.find((m) => m.id === materialId)
        const materialName = material ? `${material.kode_barang} - ${material.nama_barang}` : `ID ${materialId}`
        Swal.fire({
          icon: 'warning',
          title: 'Quantity Melebihi Stok',
          text: `Quantity pada baris ${i + 1} (${materialName}) tidak boleh melebihi stok saat ini (${currentStock}).`,
        })
        return
      }
    }

    try {
      setLoading(true)
      await inventoryService.createStockOutBulk(
        {
          mandor_id: parseInt(formData.mandor_id, 10),
          tanggal_keluar: formData.tanggal_keluar,
          items: numberItems,
          nomor_surat_permintaan: selectedNomorSurat || undefined,
        },
        [], // evidenceFiles - tidak digunakan lagi
        suratPermohonanFiles,
        suratSerahTerimaFiles
      )

      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Barang keluar (bulk) berhasil dicatat',
        timer: 2000,
      })

      // Reset form
      setFormData({
        mandor_id: '',
        tanggal_keluar: getTodayDate(),
      })
      setItems([{ material_id: '', quantity: '' }])
      setMaterialStocks({})
      setSuratPermohonanFiles([])
      setSuratSerahTerimaFiles([])
      setSelectedNomorSurat('')
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || error.response?.data?.message || 'Gagal mencatat barang keluar',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Input Barang Keluar</h1>
        <button
          type="button"
          onClick={() => navigate('/inventory/stock-out/list')}
          className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          Daftar Barang Keluar
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Mandor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mandor <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.mandor_id}
            onChange={(e) => setFormData({ ...formData, mandor_id: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Pilih Mandor</option>
            {mandors
              .filter((mandor) => mandor.is_active === 1)
              .map((mandor) => (
                <option key={mandor.id} value={mandor.id}>
                  {mandor.nama}
                </option>
              ))}
          </select>
        </div>

        {/* Surat Permintaan */}
        <div className="relative" ref={suratPermintaanDropdownRef}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Pilih Nomor Surat Permintaan (Opsional)
          </label>
          <div className="relative">
            <input
              type="text"
              value={isSuratPermintaanDropdownOpen ? searchSuratPermintaanTerm : selectedNomorSurat}
              onChange={(e) => {
                setSearchSuratPermintaanTerm(e.target.value)
                if (!isSuratPermintaanDropdownOpen) {
                  setIsSuratPermintaanDropdownOpen(true)
                }
              }}
              onFocus={() => {
                setIsSuratPermintaanDropdownOpen(true)
                if (!searchSuratPermintaanTerm && selectedNomorSurat) {
                  setSearchSuratPermintaanTerm(selectedNomorSurat)
                }
              }}
              onBlur={() => {
                setTimeout(() => {
                  if (suratPermintaanDropdownRef.current && !suratPermintaanDropdownRef.current.contains(document.activeElement)) {
                    setIsSuratPermintaanDropdownOpen(false)
                    setSearchSuratPermintaanTerm('')
                  }
                }, 200)
              }}
              placeholder="Cari nomor surat permintaan..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
              disabled={loadingSuratPermintaan}
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              {loadingSuratPermintaan ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              ) : (
                <svg
                  className={`h-5 w-5 text-gray-400 transition-transform ${isSuratPermintaanDropdownOpen ? 'transform rotate-180' : ''}`}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M19 9l-7 7-7-7" />
                </svg>
              )}
            </div>
          </div>

          {isSuratPermintaanDropdownOpen && (
            <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
              {filteredSuratPermintaans.length > 0 ? (
                <ul className="py-1">
                  <li
                    onClick={() => {
                      handleSelectNomorSurat('')
                      setIsSuratPermintaanDropdownOpen(false)
                      setSearchSuratPermintaanTerm('')
                    }}
                    className={`px-4 py-2 cursor-pointer hover:bg-blue-50 transition-colors ${
                      selectedNomorSurat === '' ? 'bg-blue-100 font-semibold' : ''
                    }`}
                  >
                    <span className="text-gray-500">-- Kosongkan pilihan --</span>
                  </li>
                  {filteredSuratPermintaans.map((sp) => (
                    <li
                      key={sp.id}
                      onClick={() => {
                        handleSelectNomorSurat(sp.nomor_surat)
                        setIsSuratPermintaanDropdownOpen(false)
                        setSearchSuratPermintaanTerm('')
                      }}
                      className={`px-4 py-2 cursor-pointer hover:bg-blue-50 transition-colors ${
                        selectedNomorSurat === sp.nomor_surat ? 'bg-blue-100 font-semibold' : ''
                      }`}
                    >
                      {sp.nomor_surat}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="px-4 py-2 text-gray-500 text-sm">
                  {searchSuratPermintaanTerm ? 'Tidak ada hasil' : 'Tidak ada data surat permintaan'}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Items (Material + Quantity) */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Daftar Item <span className="text-red-500">*</span>
            </label>
            <button
              type="button"
              onClick={() => setItems((prev) => [...prev, { material_id: '', quantity: '' }])}
              className="px-3 py-1.5 bg-emerald-600 text-white rounded-md hover:bg-emerald-700"
            >
              Tambah Baris
            </button>
          </div>

          <div className="overflow-x-auto">
            <div className="min-w-[600px] grid grid-cols-12 gap-3">
              <div className="col-span-7 text-xs font-semibold text-gray-600">Material</div>
              <div className="col-span-4 text-xs font-semibold text-gray-600">Quantity</div>
              <div className="col-span-1" />

              {items.map((row, idx) => {
                const materialId = parseInt(row.material_id || '0')
                const currentStock = materialStocks[materialId]
                const isStockZero = currentStock !== undefined && currentStock !== null && currentStock <= 0
                const material = materials.find((m) => m.id === materialId)

                return (
                  <div key={`row-${idx}`} className="contents">
                    <div className="col-span-7">
                      <select
                        value={row.material_id}
                        onChange={(e) => {
                          const v = e.target.value
                          setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, material_id: v, quantity: '' } : it)))
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Pilih Material</option>
                        {materials
                          .filter((material) => material.is_active === 1)
                          .map((material) => (
                            <option key={material.id} value={material.id.toString()}>
                              {material.kode_barang} - {material.nama_barang}
                            </option>
                          ))}
                      </select>
                    </div>
                    <div className="col-span-4">
                      <input
                        type="number"
                        step="0.01"
                        min="0.01"
                        max={currentStock !== undefined && currentStock !== null && currentStock > 0 ? currentStock : undefined}
                        value={row.quantity}
                        onChange={(e) => {
                          const raw = e.target.value
                          // Normalisasi segera: angka decimal >=0.01 dan <= stok saat ini (jika tersedia)
                          const parsed = parseFloat(raw)
                          let next = raw
                          if (!isNaN(parsed)) {
                            let clamped = Math.max(0.01, parsed)
                            if (currentStock !== undefined && currentStock !== null && currentStock > 0) {
                              clamped = Math.min(clamped, currentStock)
                            }
                            next = clamped.toString()
                          } else if (raw === '') {
                            next = ''
                          }
                          setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, quantity: next } : it)))
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Qty"
                        disabled={isStockZero}
                      />
                      {currentStock !== undefined && currentStock !== null && (
                        <p className={`mt-1 text-xs ${currentStock <= 0 ? 'text-red-600' : 'text-green-600'}`}>
                          Stok: <span className="font-semibold">{formatDecimal(currentStock)}</span> {material?.satuan || ''}
                        </p>
                      )}
                    </div>
                    <div className="col-span-1 flex items-center justify-end">
                      <button
                        type="button"
                        onClick={() => setItems((prev) => prev.filter((_, i) => i !== idx))}
                        className="px-3 py-2 border border-red-300 text-red-600 rounded-md hover:bg-red-50"
                        disabled={items.length === 1}
                      >
                        Hapus
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Tanggal Keluar */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tanggal Keluar <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={formData.tanggal_keluar}
            onChange={(e) => setFormData({ ...formData, tanggal_keluar: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        {/* Upload Surat Permohonan dan Surat Serah Terima - Inline */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Surat Permohonan Upload */}
          <EvidenceUpload
            files={suratPermohonanFiles}
            onChange={setSuratPermohonanFiles}
            maxFiles={5}
            maxSize={5}
            label="Upload Evidence Surat Permohonan dari Mandor (Maksimal 5 file, 5MB per file)"
            inputId="surat-permohonan-upload"
          />

          {/* Surat Serah Terima Upload */}
          <EvidenceUpload
            files={suratSerahTerimaFiles}
            onChange={setSuratSerahTerimaFiles}
            maxFiles={5}
            maxSize={5}
            label="Upload Surat Serah Terima Gudang (Maksimal 5 file, 5MB per file)"
            inputId="surat-serah-terima-upload"
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-4 pt-4">
          <button
            type="button"
            onClick={() => navigate('/inventory')}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Batal
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Menyimpan...' : 'Simpan'}
          </button>
        </div>
      </form>
    </div>
  )
}

