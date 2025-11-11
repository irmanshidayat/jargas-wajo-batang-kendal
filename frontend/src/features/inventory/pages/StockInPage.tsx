import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { inventoryService, Material } from '../services/inventoryService'
import EvidenceUpload from '../components/EvidenceUpload'
import Swal from 'sweetalert2'
import { getTodayDate } from '../../../utils/helpers'
import {
  sanitizeItems,
  validateItemsNotEmpty,
  validateAllQuantities,
  hasDuplicateMaterials,
  showValidationErrorIfInvalid,
  showDuplicateErrorIfExists,
  convertItemsToNumbers,
} from '../utils/formValidation'

export default function StockInPage() {
  const navigate = useNavigate()
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    nomor_invoice: '',
    tanggal_masuk: getTodayDate(),
  })
  const [items, setItems] = useState<Array<{ material_id: string; quantity: string }>>([
    { material_id: '', quantity: '' },
  ])
  const [suratJalanFiles, setSuratJalanFiles] = useState<File[]>([])
  const [materialDatangFiles, setMaterialDatangFiles] = useState<File[]>([])

  useEffect(() => {
    loadMaterials()
  }, [])

  const loadMaterials = async () => {
    try {
      const response = await inventoryService.getMaterials(1, 1000)
      const items = Array.isArray((response as any)?.data)
        ? (response as any).data
        : Array.isArray(response)
          ? response
          : ((response as any)?.data?.items || (response as any)?.data || (response as any)?.items || [])
      setMaterials(items as Material[])
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || error.response?.data?.message || 'Gagal memuat data materials',
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // Validasi dasar
    if (!formData.nomor_invoice || !formData.tanggal_masuk) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Nomor invoice dan tanggal masuk wajib diisi',
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

    try {
      setLoading(true)
      // DEBUG: Log nilai sebelum dikirim
      const itemsToSend = convertItemsToNumbers(sanitized)
      
      console.group('🔍 [DEBUG STOCK-IN] Quantity Validation')
      console.log('📥 Items original dari form:', JSON.stringify(items, null, 2))
      console.log('🧹 Items setelah sanitize:', JSON.stringify(sanitized, null, 2))
      console.log('🔄 Items setelah convert (akan dikirim):', JSON.stringify(itemsToSend, null, 2))
      
      // Verifikasi quantity masih sesuai
      let allValid = true
      for (let i = 0; i < itemsToSend.length; i++) {
        const originalQty = sanitized[i].quantity
        const convertedQty = itemsToSend[i].quantity
        const parsedOriginal = parseFloat(originalQty)
        
        console.log(`\n📊 Item ${i + 1} Verification:`)
        console.log(`   Original (string): "${originalQty}"`)
        console.log(`   Parsed (number): ${parsedOriginal}`)
        console.log(`   Converted (final): ${convertedQty}`)
        console.log(`   Match: ${Math.abs(parsedOriginal - convertedQty) < 0.001 ? '✅' : '❌'}`)
        
        if (Math.abs(parsedOriginal - convertedQty) >= 0.001) {
          console.error(`❌ [ERROR] Quantity mismatch! Original: ${originalQty}, Converted: ${convertedQty}`)
          allValid = false
        }
      }
      console.groupEnd()
      
      if (!allValid) {
        Swal.fire({
          icon: 'error',
          title: 'Error Validasi',
          text: `Terjadi kesalahan konversi quantity. Silakan cek console untuk detail.`,
        })
        return
      }
      
      await inventoryService.createStockInBulk(
        {
          nomor_invoice: formData.nomor_invoice,
          tanggal_masuk: formData.tanggal_masuk,
          items: itemsToSend,
        },
        [], // evidenceFiles - tidak digunakan lagi
        suratJalanFiles,
        materialDatangFiles
      )

      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Barang masuk (bulk) berhasil dicatat',
        timer: 2000,
      })

      // Reset form
      setFormData({
        nomor_invoice: '',
        tanggal_masuk: getTodayDate(),
      })
      setItems([{ material_id: '', quantity: '' }])
      setSuratJalanFiles([])
      setMaterialDatangFiles([])
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || error.response?.data?.message || 'Gagal mencatat barang masuk',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Input Barang Masuk</h1>
        <button
          type="button"
          onClick={() => navigate('/inventory/stock-in/list')}
          className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          Daftar Barang Masuk
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Nomor Invoice */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nomor Invoice / DO <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.nomor_invoice}
            onChange={(e) => setFormData({ ...formData, nomor_invoice: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Masukkan nomor invoice dari gudang pusat"
            required
          />
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

              {items.map((row, idx) => (
                <div key={`row-${idx}`} className="contents">
                  <div className="col-span-7">
                    <select
                      value={row.material_id}
                      onChange={(e) => {
                        const v = e.target.value
                        setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, material_id: v } : it)))
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Pilih Material</option>
                      {materials.map((material) => (
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
                      value={row.quantity}
                      onChange={(e) => {
                        const v = e.target.value
                        setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, quantity: v } : it)))
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Qty"
                    />
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
              ))}
            </div>
          </div>
        </div>

        {/* Tanggal Masuk */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tanggal Masuk <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={formData.tanggal_masuk}
            onChange={(e) => setFormData({ ...formData, tanggal_masuk: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        {/* Upload Surat Jalan dan Material Datang - Inline */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Surat Jalan Upload */}
          <EvidenceUpload
            files={suratJalanFiles}
            onChange={setSuratJalanFiles}
            maxFiles={5}
            maxSize={5}
            label="Upload Surat Jalan (Maksimal 5 file, 5MB per file)"
            inputId="surat-jalan-upload"
          />

          {/* Material Datang Upload */}
          <EvidenceUpload
            files={materialDatangFiles}
            onChange={setMaterialDatangFiles}
            maxFiles={5}
            maxSize={5}
            label="Upload Material Datang (Maksimal 5 file, 5MB per file)"
            inputId="material-datang-upload"
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

