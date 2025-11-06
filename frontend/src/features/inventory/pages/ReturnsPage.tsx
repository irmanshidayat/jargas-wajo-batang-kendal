import { useState, useEffect, useRef, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { inventoryService, Material, Mandor, StockOut } from '../services/inventoryService'
import { extractItems } from '@/utils/api'
import EvidenceUpload from '../components/EvidenceUpload'
import Swal from 'sweetalert2'
import { getTodayDate, formatDecimal } from '@/utils/helpers'
import {
  validateQuantity,
  parseQuantityWithFlag,
} from '../utils/formValidation'
import {
  computeStockOutSisa,
  formatStockOutOptionLabel,
  formatStockOutInfoCard,
  isStockOutFull,
  getStockOutDropdownPlaceholder,
} from '../utils/returnsHelpers'

export default function ReturnsPage() {
  const navigate = useNavigate()
  const [materials, setMaterials] = useState<Material[]>([])
  const [mandors, setMandors] = useState<Mandor[]>([])
  const [stockOuts, setStockOuts] = useState<StockOut[]>([])
  const [loadingStockOuts, setLoadingStockOuts] = useState(false)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    mandor_id: '',
    tanggal_kembali: getTodayDate(),
  })
  const [stockOutRows, setStockOutRows] = useState<Array<{ nomor_barang_keluar: string }>>([
    { nomor_barang_keluar: '' },
  ])
  const [items, setItems] = useState<Array<{ material_id: string; quantity_kembali: string; quantity_kondisi_baik: string; quantity_kondisi_reject: string }>>([
    { material_id: '', quantity_kembali: '', quantity_kondisi_baik: '', quantity_kondisi_reject: '' },
  ])
  const [evidenceFiles, setEvidenceFiles] = useState<File[]>([])
  const isManualEditRef = useRef(false) // Track apakah user sudah edit manual

  useEffect(() => {
    loadMaterials()
    loadMandors()
  }, [])

  // Load stock outs berdasarkan mandor yang dipilih
  useEffect(() => {
    if (formData.mandor_id) {
      loadStockOutsByMandor(parseInt(formData.mandor_id))
    } else {
      setStockOuts([])
      setStockOutRows([{ nomor_barang_keluar: '' }])
    }
  }, [formData.mandor_id])

  // Map nomor_barang_keluar ke StockOut untuk lookup cepat (optimasi dengan useMemo)
  const stockOutByNomorMap = useMemo(() => {
    const map = new Map<string, StockOut>()
    stockOuts.forEach(so => {
      if (so.nomor_barang_keluar) {
        map.set(so.nomor_barang_keluar, so)
      }
    })
    return map
  }, [stockOuts])

  // Auto-fill items ketika nomor barang keluar dipilih
  useEffect(() => {
    // Ambil semua stock out yang dipilih (non-empty) - gunakan map untuk performa lebih baik
    const selectedStockOuts = stockOutRows
      .map(row => row.nomor_barang_keluar)
      .filter(nomor => nomor !== '')
      .map(nomor => stockOutByNomorMap.get(nomor))
      .filter((so): so is StockOut => so !== undefined)
    
    if (selectedStockOuts.length > 0) {
      // Auto-fill items dengan material dan quantity dari semua stock out yang dipilih
      const autoFilledItems = selectedStockOuts.map(selectedStockOut => {
        const sisaInfo = computeStockOutSisa(selectedStockOut)
        
        if (selectedStockOut.material_id && sisaInfo.quantity_sisa_kembali > 0) {
          return {
            material_id: selectedStockOut.material_id.toString(),
            quantity_kembali: sisaInfo.quantity_sisa_kembali.toString(),
            quantity_kondisi_baik: '',
            quantity_kondisi_reject: ''
          }
        } else {
          return {
            material_id: selectedStockOut.material_id?.toString() || '',
            quantity_kembali: '',
            quantity_kondisi_baik: '',
            quantity_kondisi_reject: ''
          }
        }
      })
      
      // Auto-fill hanya jika belum ada manual edit
      if (!isManualEditRef.current) {
        setItems(autoFilledItems.length > 0 ? autoFilledItems : [{ material_id: '', quantity_kembali: '', quantity_kondisi_baik: '', quantity_kondisi_reject: '' }])
      }
    } else {
      // Reset items hanya jika semua nomor barang keluar di-reset DAN belum ada manual edit
      if (stockOutRows.every(row => row.nomor_barang_keluar === '')) {
        if (!isManualEditRef.current) {
          setItems([{ material_id: '', quantity_kembali: '', quantity_kondisi_baik: '', quantity_kondisi_reject: '' }])
        }
      }
    }
  }, [stockOutRows, stockOutByNomorMap])

  // Reset manual edit flag ketika stock out rows di-reset
  useEffect(() => {
    if (stockOutRows.every(row => row.nomor_barang_keluar === '')) {
      isManualEditRef.current = false
    }
  }, [stockOutRows])

  const loadStockOutsByMandor = async (mandorId: number) => {
    try {
      setLoadingStockOuts(true)
      const response = await inventoryService.getStockOutsByMandor(mandorId)
      const items = extractItems<StockOut>(response)
      setStockOuts(items)
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error?.response?.data?.detail || 'Gagal memuat data barang keluar',
      })
      setStockOuts([])
    } finally {
      setLoadingStockOuts(false)
    }
  }

  const loadMaterials = async () => {
    try {
      const response = await inventoryService.getMaterials(1, 1000)
      setMaterials(extractItems<Material>(response))
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
      setMandors(extractItems<Mandor>(response))
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Gagal memuat data mandors',
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validasi dasar
    const selectedStockOutNumbers = stockOutRows
      .map(row => row.nomor_barang_keluar)
      .filter(nomor => nomor !== '')
    
    if (!formData.mandor_id || !formData.tanggal_kembali || selectedStockOutNumbers.length === 0) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Mandor, Nomor Barang Keluar, dan tanggal kembali wajib diisi',
      })
      return
    }

    // Validasi items
    console.log('[DEBUG] Original items:', JSON.stringify(items, null, 2))
    
    const sanitized = items
      .map((it) => ({ 
        material_id: it.material_id.trim(), 
        quantity_kembali: it.quantity_kembali.trim(),
        quantity_kondisi_baik: it.quantity_kondisi_baik.trim(),
        quantity_kondisi_reject: it.quantity_kondisi_reject.trim()
      }))
      .filter((it) => it.material_id !== '' && it.quantity_kembali !== '')
    
    console.log('[DEBUG] After sanitize:', JSON.stringify(sanitized, null, 2))

    if (sanitized.length === 0) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Minimal 1 baris material dan quantity kembali harus diisi',
      })
      return
    }

    // Validasi quantity kembali >= 0.01 dan bisa decimal
    for (let i = 0; i < sanitized.length; i++) {
      const validation = validateQuantity(sanitized[i].quantity_kembali, i + 1)
      if (!validation.isValid) {
        const errorMsg = validation.errorMessage?.replace('Quantity', 'Quantity kembali') || ''
        Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: errorMsg,
        })
        return
      }
    }

    // Validasi quantity kondisi baik dan reject
    for (let i = 0; i < sanitized.length; i++) {
      const quantityKembali = parseFloat(sanitized[i].quantity_kembali)
      
      console.log(`[DEBUG] Baris ${i + 1} - Raw values:`, {
        quantity_kembali: sanitized[i].quantity_kembali,
        quantity_kondisi_baik: sanitized[i].quantity_kondisi_baik,
        quantity_kondisi_reject: sanitized[i].quantity_kondisi_reject,
        quantity_kondisi_baik_type: typeof sanitized[i].quantity_kondisi_baik,
        quantity_kondisi_reject_type: typeof sanitized[i].quantity_kondisi_reject,
        quantity_kondisi_baik_length: sanitized[i].quantity_kondisi_baik?.length,
        quantity_kondisi_reject_length: sanitized[i].quantity_kondisi_reject?.length,
      })
      
      // Parse quantity dengan handling untuk empty string, whitespace, dan "0"
      const parsedBaik = parseQuantityWithFlag(sanitized[i].quantity_kondisi_baik)
      const parsedReject = parseQuantityWithFlag(sanitized[i].quantity_kondisi_reject)
      const quantityKondisiBaik = parsedBaik.value
      const quantityKondisiReject = parsedReject.value
      
      console.log(`[DEBUG] Baris ${i + 1} - Parsed values:`, {
        quantityKembali,
        quantityKondisiBaik,
        quantityKondisiReject,
        baikWasFilled: parsedBaik.wasFilled,
        rejectWasFilled: parsedReject.wasFilled,
        total: quantityKondisiBaik + quantityKondisiReject,
        condition: `baik <= 0: ${quantityKondisiBaik <= 0}, reject <= 0: ${quantityKondisiReject <= 0}`
      })

      // Validasi: minimal salah satu harus diisi (> 0) DAN total tidak boleh 0
      const totalKondisi = quantityKondisiBaik + quantityKondisiReject
      if (totalKondisi <= 0) {
        console.error(`[DEBUG] Validation failed for baris ${i + 1}:`, {
          quantityKondisiBaik,
          quantityKondisiReject,
          baikWasFilled: parsedBaik.wasFilled,
          rejectWasFilled: parsedReject.wasFilled,
          total: totalKondisi,
          condition: 'total <= 0'
        })
        Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Baris ${i + 1}: Total quantity kondisi baik dan reject harus lebih dari 0. Saat ini total: ${totalKondisi}. Silakan isi salah satu atau kedua field dengan nilai yang sesuai (total tidak boleh 0).`,
        })
        return
      }

      // Validasi: quantity kondisi baik dan reject harus >= 0 jika diisi
      if (quantityKondisiBaik < 0 || quantityKondisiReject < 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Baris ${i + 1}: Quantity kondisi baik dan reject tidak boleh negatif`,
        })
        return
      }

      // Validasi: jumlah quantity kondisi baik + reject tidak boleh lebih dari quantity_kembali
      if (totalKondisi > quantityKembali) {
        Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Baris ${i + 1}: Jumlah quantity kondisi baik (${quantityKondisiBaik}) + kondisi reject (${quantityKondisiReject}) = ${totalKondisi} tidak boleh lebih dari quantity kembali (${quantityKembali})`,
        })
        return
      }
    }

    try {
      setLoading(true)
      
      // Buat mapping material_id ke stock out untuk mendapatkan nomor_barang_keluar
      const materialToStockOutMap = new Map<number, StockOut>()
      selectedStockOutNumbers.forEach(nomor => {
        const stockOut = stockOuts.find(so => so.nomor_barang_keluar === nomor)
        if (stockOut && stockOut.material_id) {
          materialToStockOutMap.set(stockOut.material_id, stockOut)
        }
      })
      
      // Submit setiap item secara sequential
      let successCount = 0
      let errorCount = 0

      for (let i = 0; i < sanitized.length; i++) {
        try {
          const materialId = parseInt(sanitized[i].material_id, 10)
          const matchingStockOut = materialToStockOutMap.get(materialId)
          const nomorBarangKeluar = matchingStockOut?.nomor_barang_keluar || selectedStockOutNumbers[0] // Fallback ke stock out pertama jika tidak ditemukan
          
          // Parse quantity kondisi baik dan reject dari item
          // Gunakan parseQuantityWithFlag untuk konsisten dengan validasi sebelumnya
          const parsedBaikSubmit = parseQuantityWithFlag(sanitized[i].quantity_kondisi_baik)
          const parsedRejectSubmit = parseQuantityWithFlag(sanitized[i].quantity_kondisi_reject)
          
          // Jika wasFilled = true, kirim nilai (termasuk 0), jika false = undefined (optional)
          const quantityKondisiBaik = parsedBaikSubmit.wasFilled ? parsedBaikSubmit.value : undefined
          const quantityKondisiReject = parsedRejectSubmit.wasFilled ? parsedRejectSubmit.value : undefined

          await inventoryService.createReturn(
            {
              mandor_id: parseInt(formData.mandor_id, 10),
              material_id: materialId,
              quantity_kembali: parseFloat(sanitized[i].quantity_kembali),
              quantity_kondisi_baik: quantityKondisiBaik,
              quantity_kondisi_reject: quantityKondisiReject,
              tanggal_kembali: formData.tanggal_kembali,
              nomor_barang_keluar: nomorBarangKeluar,
            },
            i === 0 ? evidenceFiles : [] // Hanya attach evidence pada item pertama
          )
          successCount++
        } catch (error: any) {
          errorCount++
          console.error(`Error creating return for item ${i + 1}:`, error)
          const errorMessage = error?.response?.data?.detail || error?.message || 'Gagal mencatat retur barang'
          console.error(`Error detail for item ${i + 1}:`, errorMessage)
          
          // Jika ini item pertama dan ada error, tampilkan error message
          if (i === 0 && errorCount === 1) {
            await Swal.fire({
              icon: 'error',
              title: 'Error',
              text: errorMessage,
            })
            setLoading(false)
            return
          }
        }
      }

      if (errorCount > 0) {
        await Swal.fire({
          icon: 'warning',
          title: 'Peringatan',
          text: `${successCount} item berhasil dicatat, ${errorCount} item gagal`,
        })
      } else {
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: `${successCount} item retur berhasil dicatat`,
          timer: 2000,
        })
        // Redirect ke halaman list setelah berhasil
        navigate('/inventory/returns')
        return
      }

      // Reset form jika ada error
      setFormData({
        mandor_id: '',
        tanggal_kembali: getTodayDate(),
      })
      setStockOuts([])
      setStockOutRows([{ nomor_barang_keluar: '' }])
      setItems([{ material_id: '', quantity_kembali: '', quantity_kondisi_baik: '', quantity_kondisi_reject: '' }])
      setEvidenceFiles([])
      isManualEditRef.current = false
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || 'Gagal mencatat retur barang',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Input Retur Barang</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Mandor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mandor <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.mandor_id}
            onChange={(e) => {
              setFormData({ 
                ...formData, 
                mandor_id: e.target.value
              })
              // Reset stock out rows ketika mandor berubah
              setStockOutRows([{ nomor_barang_keluar: '' }])
              isManualEditRef.current = false
            }}
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

        {/* Nomor Barang Keluar - Multiple rows */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Nomor Barang Keluar <span className="text-red-500">*</span>
            </label>
            <button
              type="button"
              onClick={() => setStockOutRows([...stockOutRows, { nomor_barang_keluar: '' }])}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              disabled={!formData.mandor_id || loadingStockOuts}
            >
              Tambah Baris
            </button>
          </div>

          <div className="overflow-x-auto">
            <div className="min-w-[600px] grid grid-cols-12 gap-3">
              <div className="col-span-11 text-xs font-semibold text-gray-600">Nomor Barang Keluar</div>
              <div className="col-span-1"></div>

              {stockOutRows.map((row, idx) => {
                const selectedStockOut = row.nomor_barang_keluar
                  ? stockOuts.find(so => so.nomor_barang_keluar === row.nomor_barang_keluar)
                  : null
                
                return (
                  <div key={`stockout-row-${idx}`} className="contents">
                    <div className="col-span-11">
                      <select
                        value={row.nomor_barang_keluar}
                        onChange={(e) => {
                          const newRows = stockOutRows.map((r, i) => 
                            i === idx ? { ...r, nomor_barang_keluar: e.target.value } : r
                          )
                          setStockOutRows(newRows)
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                        disabled={!formData.mandor_id || loadingStockOuts}
                        required={idx === 0}
                      >
                        <option value="">
                          {getStockOutDropdownPlaceholder({
                            loading: loadingStockOuts,
                            hasMandor: !!formData.mandor_id,
                            hasItems: stockOuts.length > 0,
                            isRequired: idx === 0,
                          })}
                        </option>
                        {stockOuts.map((stockOut) => {
                          const full = isStockOutFull(stockOut)
                          
                          return (
                            <option 
                              key={stockOut.id} 
                              value={stockOut.nomor_barang_keluar}
                              disabled={full}
                              style={full ? { color: '#9CA3AF' } : {}}
                            >
                              {formatStockOutOptionLabel(stockOut)}
                            </option>
                          )
                        })}
                      </select>
                      {selectedStockOut && (() => {
                        const info = formatStockOutInfoCard(selectedStockOut)
                        return (
                          <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-xs text-blue-700">
                              Material: <strong>{info.materialName}</strong>
                              {' | '}Qty: <strong>{formatDecimal(info.quantity)}</strong>
                              {' | '}Terpasang: <strong>{formatDecimal(info.quantity_terpasang)}</strong>
                              {' | '}Sisa: <strong className="text-green-700">{formatDecimal(info.quantity_sisa_kembali)}</strong>
                              {' | '}Sudah kembali: <strong>{formatDecimal(info.quantity_sudah_kembali)}</strong>
                            </p>
                          </div>
                        )
                      })()}
                    </div>
                    <div className="col-span-1 flex items-center justify-end">
                      <button
                        type="button"
                        onClick={() => setStockOutRows((prev) => prev.filter((_, i) => i !== idx))}
                        className="px-3 py-2 border border-red-300 text-red-600 rounded-md hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={stockOutRows.length === 1}
                        title={stockOutRows.length === 1 ? 'Minimal harus ada 1 baris' : 'Hapus baris'}
                      >
                        Hapus
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {formData.mandor_id && stockOuts.length > 0 && (
            <p className="mt-2 text-sm text-gray-500">
              Pilih nomor barang keluar untuk mandor ini. Total: {stockOuts.length} item tersedia
            </p>
          )}
        </div>

        {/* Items (Material + Quantity Kembali) */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Daftar Item <span className="text-red-500">*</span>
            </label>
            <button
              type="button"
              onClick={() => {
                isManualEditRef.current = true
                setItems((prev) => [...prev, { material_id: '', quantity_kembali: '', quantity_kondisi_baik: '', quantity_kondisi_reject: '' }])
              }}
              className="px-3 py-1.5 bg-emerald-600 text-white rounded-md hover:bg-emerald-700"
            >
              Tambah Baris
            </button>
          </div>

          <div className="overflow-x-auto">
            <div className="min-w-[800px] grid grid-cols-12 gap-3">
              <div className="col-span-5 text-xs font-semibold text-gray-600">Material</div>
              <div className="col-span-2 text-xs font-semibold text-gray-600">Quantity</div>
              <div className="col-span-2 text-xs font-semibold text-gray-600">Kondisi Baik</div>
              <div className="col-span-2 text-xs font-semibold text-gray-600">Kondisi Reject</div>
              <div className="col-span-1"></div>

              {items.map((row, idx) => {
                // Cek apakah ini item yang auto-filled dari stock out
                const selectedStockOutNumbers = stockOutRows
                  .map(r => r.nomor_barang_keluar)
                  .filter(nomor => nomor !== '')
                
                const matchingStockOut = row.material_id
                  ? stockOuts.find(so => 
                      so.material_id?.toString() === row.material_id &&
                      selectedStockOutNumbers.includes(so.nomor_barang_keluar)
                    )
                  : null
                
                const isAutoFilled = !!matchingStockOut
                const sisaInfo = matchingStockOut ? computeStockOutSisa(matchingStockOut) : null
                
                return (
                <div key={`row-${idx}`} className="contents">
                  <div className="col-span-5">
                    <select
                      value={row.material_id}
                      onChange={(e) => {
                        const v = e.target.value
                        isManualEditRef.current = true
                        setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, material_id: v } : it)))
                      }}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                        isAutoFilled ? 'border-blue-300 bg-blue-50' : 'border-gray-300'
                      }`}
                      disabled={isAutoFilled} // Material tidak bisa diubah jika auto-filled
                      title={isAutoFilled ? 'Material ini sesuai dengan stock out yang dipilih' : ''}
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
                  <div className="col-span-2">
                    <input
                      type="number"
                      step="0.01"
                      min="0.01"
                      max={sisaInfo?.quantity_sisa_kembali}
                      value={row.quantity_kembali}
                      onChange={(e) => {
                        const v = e.target.value
                        isManualEditRef.current = true
                        setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, quantity_kembali: v } : it)))
                      }}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                        isAutoFilled ? 'border-blue-300 bg-blue-50' : 'border-gray-300'
                      }`}
                      placeholder="Qty"
                      title={
                        isAutoFilled && sisaInfo
                          ? `Maksimal: ${sisaInfo.quantity_sisa_kembali} (sisa yang bisa dikembalikan)`
                          : ''
                      }
                    />
                  </div>
                  <div className="col-span-2">
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={row.quantity_kondisi_baik}
                      onChange={(e) => {
                        const v = e.target.value
                        console.log(`[DEBUG] onChange quantity_kondisi_baik - Baris ${idx + 1}:`, {
                          rawValue: e.target.value,
                          processedValue: v,
                          type: typeof v,
                          isEmpty: v === '',
                          isZero: v === '0',
                          currentState: row.quantity_kondisi_baik
                        })
                        isManualEditRef.current = true
                        setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, quantity_kondisi_baik: v } : it)))
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Masukkan quantity kondisi baik"
                    />
                  </div>
                  <div className="col-span-2">
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={row.quantity_kondisi_reject}
                      onChange={(e) => {
                        const v = e.target.value
                        console.log(`[DEBUG] onChange quantity_kondisi_reject - Baris ${idx + 1}:`, {
                          rawValue: e.target.value,
                          processedValue: v,
                          type: typeof v,
                          isEmpty: v === '',
                          isZero: v === '0',
                          currentState: row.quantity_kondisi_reject
                        })
                        isManualEditRef.current = true
                        setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, quantity_kondisi_reject: v } : it)))
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Masukkan quantity kondisi reject"
                    />
                  </div>
                  <div className="col-span-1 flex items-center justify-end">
                    <button
                      type="button"
                      onClick={() => {
                        isManualEditRef.current = true
                        setItems((prev) => prev.filter((_, i) => i !== idx))
                      }}
                      className="px-3 py-2 border border-red-300 text-red-600 rounded-md hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={items.length === 1 || isAutoFilled} // Jangan bisa hapus jika hanya 1 item atau auto-filled
                      title={isAutoFilled ? 'Item ini dari stock out yang dipilih, tidak bisa dihapus' : ''}
                    >
                      Hapus
                    </button>
                  </div>
                </div>
              )})}
            </div>
          </div>
        </div>


        {/* Tanggal Kembali */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tanggal Kembali <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={formData.tanggal_kembali}
            onChange={(e) => setFormData({ ...formData, tanggal_kembali: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        {/* Evidence Upload */}
        <EvidenceUpload
          files={evidenceFiles}
          onChange={setEvidenceFiles}
          maxFiles={5}
          maxSize={5}
        />

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

