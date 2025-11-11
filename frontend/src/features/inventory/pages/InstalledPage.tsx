import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { inventoryService, Material, Mandor, StockOut } from '../services/inventoryService'
import { extractItems } from '@/utils/api'
import { getSisaPasang, getInstalledMaxQty, formatInstalledStockOutOption } from '../utils/installedHelpers'
import EvidenceUpload from '../components/EvidenceUpload'
import Swal from 'sweetalert2'
import { getTodayDate, formatDecimal } from '@/utils/helpers'
import {
  sanitizeItems,
  validateItemsNotEmpty,
  validateAllQuantities,
  showValidationErrorIfInvalid,
  convertItemsToNumbers,
} from '../utils/formValidation'

export default function InstalledPage() {
  const navigate = useNavigate()
  const [materials, setMaterials] = useState<Material[]>([])
  const [mandors, setMandors] = useState<Mandor[]>([])
  const [stockOuts, setStockOuts] = useState<StockOut[]>([])
  const [loadingStockOuts, setLoadingStockOuts] = useState(false)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    mandor_id: '',
    tanggal_pasang: getTodayDate(),
    no_register: '',
  })
  const [stockOutRows, setStockOutRows] = useState<Array<{ nomor_barang_keluar: string }>>([
    { nomor_barang_keluar: '' },
  ])
  const [items, setItems] = useState<Array<{ material_id: string; quantity: string }>>([
    { material_id: '', quantity: '' },
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

  // Auto-fill items ketika nomor barang keluar dipilih
  useEffect(() => {
    // Ambil semua stock out yang dipilih (non-empty)
    const selectedStockOuts = stockOutRows
      .map(row => row.nomor_barang_keluar)
      .filter(nomor => nomor !== '')
      .map(nomor => stockOuts.find(so => so.nomor_barang_keluar === nomor))
      .filter((so): so is StockOut => so !== undefined)
    
    if (selectedStockOuts.length > 0) {
      // Auto-fill items dengan material dan quantity dari semua stock out yang dipilih
      const autoFilledItems = selectedStockOuts.map(selectedStockOut => {
        // Gunakan quantity_sisa_kembali jika ada, fallback ke quantity_sisa atau quantity
        const sisaKembali = (selectedStockOut as any).quantity_sisa_kembali !== undefined 
          ? (selectedStockOut as any).quantity_sisa_kembali 
          : selectedStockOut.quantity_sisa !== undefined 
          ? selectedStockOut.quantity_sisa 
          : selectedStockOut.quantity
        
        if (selectedStockOut.material_id && sisaKembali > 0) {
          return {
            material_id: selectedStockOut.material_id.toString(),
            quantity: sisaKembali.toString(),
          }
        } else {
          return {
            material_id: selectedStockOut.material_id?.toString() || '',
            quantity: '',
          }
        }
      })
      
      // Auto-fill hanya jika belum ada manual edit
      if (!isManualEditRef.current) {
        setItems(autoFilledItems.length > 0 ? autoFilledItems : [{ material_id: '', quantity: '' }])
      }
    } else {
      // Reset items hanya jika semua nomor barang keluar di-reset DAN belum ada manual edit
      if (stockOutRows.every(row => row.nomor_barang_keluar === '')) {
        if (!isManualEditRef.current) {
          setItems([{ material_id: '', quantity: '' }])
        }
      }
    }
  }, [stockOutRows, stockOuts])

  // Reset manual edit flag ketika stock out rows di-reset
  useEffect(() => {
    if (stockOutRows.every(row => row.nomor_barang_keluar === '')) {
      isManualEditRef.current = false
    }
  }, [stockOutRows])

  const loadStockOutsByMandor = async (mandorId: number) => {
    try {
      setLoadingStockOuts(true)
      // Tampilkan loading tanpa menunggu resolve
      Swal.fire({
        title: 'Memuat... ',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading()
        },
      })
      const response = await inventoryService.getStockOutsByMandor(mandorId)
      const items = extractItems<StockOut>(response)
      setStockOuts(items)
    } catch (error: any) {
      if (Swal.isVisible()) Swal.close()
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error?.response?.data?.detail || 'Gagal memuat data barang keluar',
      })
      setStockOuts([])
    } finally {
      setLoadingStockOuts(false)
      if (Swal.isVisible()) Swal.close()
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
    if (!formData.mandor_id || !formData.tanggal_pasang) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Mandor dan tanggal pasang wajib diisi',
      })
      return
    }

    // Validasi items
    const sanitized = sanitizeItems(items)
    
    if (!validateItemsNotEmpty(sanitized)) return
    
    // Validasi quantity
    const quantityValidation = validateAllQuantities(sanitized)
    if (!showValidationErrorIfInvalid(quantityValidation)) return

    // Validasi jika nomor barang keluar dipilih
    const selectedStockOutNumbers = stockOutRows
      .map(row => row.nomor_barang_keluar)
      .filter(nomor => nomor !== '')
    
    if (selectedStockOutNumbers.length > 0) {
      // Validasi material harus sesuai dengan stock out yang dipilih
      const selectedStockOuts = selectedStockOutNumbers
        .map(nomor => stockOuts.find(so => so.nomor_barang_keluar === nomor))
        .filter((so): so is StockOut => so !== undefined)
      
      // Buat mapping material_id ke stock out
      const materialToStockOutMap = new Map<number, StockOut>()
      selectedStockOuts.forEach(so => {
        if (so.material_id) {
          materialToStockOutMap.set(so.material_id, so)
        }
      })
      
      // Convert dan validasi setiap item harus sesuai dengan salah satu stock out
      const numberItems = convertItemsToNumbers(sanitized)
      for (let i = 0; i < numberItems.length; i++) {
        const materialId = numberItems[i].material_id
        const matchingStockOut = materialToStockOutMap.get(materialId)
        
        if (!matchingStockOut) {
          Swal.fire({
            icon: 'warning',
            title: 'Perhatian',
            text: `Material pada baris ${i + 1} harus sesuai dengan salah satu stock out yang dipilih`,
          })
          return
        }
      }
    }

    try {
      setLoading(true)
      
      // Submit setiap item secara sequential
      let successCount = 0
      let errorCount = 0

      // Buat mapping material_id ke stock out untuk mendapatkan stock_out_id
      const materialToStockOutMap = new Map<number, StockOut>()
      const selectedStockOutNumbersMap = stockOutRows
        .map(row => row.nomor_barang_keluar)
        .filter(nomor => nomor !== '')
      
      if (selectedStockOutNumbersMap.length > 0) {
        selectedStockOutNumbersMap.forEach(nomor => {
          const stockOut = stockOuts.find(so => so.nomor_barang_keluar === nomor)
          if (stockOut && stockOut.material_id) {
            materialToStockOutMap.set(stockOut.material_id, stockOut)
          }
        })
      }

      const numberItems = convertItemsToNumbers(sanitized)
      for (let i = 0; i < numberItems.length; i++) {
        try {
          const materialId = numberItems[i].material_id
          const quantity = numberItems[i].quantity
          const matchingStockOut = materialToStockOutMap.get(materialId)
          const stockOutId = matchingStockOut?.id
          
          await inventoryService.createInstalled(
            {
              material_id: materialId,
              quantity: quantity,
              tanggal_pasang: formData.tanggal_pasang,
              mandor_id: parseInt(formData.mandor_id, 10),
              stock_out_id: stockOutId,
              no_register: formData.no_register || undefined,
            },
            i === 0 ? evidenceFiles : [] // Hanya attach evidence pada item pertama
          )
          successCount++
        } catch (error: any) {
          errorCount++
          console.error(`Error creating installed for item ${i + 1}:`, error)
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
          text: `${successCount} item barang terpasang berhasil dicatat`,
          timer: 2000,
        })
        // Redirect ke halaman daftar barang terpasang setelah berhasil
        navigate('/inventory/installed')
        return
      }

      // Reset form jika ada error
      setFormData({
        mandor_id: '',
        tanggal_pasang: getTodayDate(),
        no_register: '',
      })
      setStockOuts([])
      setStockOutRows([{ nomor_barang_keluar: '' }])
      setItems([{ material_id: '', quantity: '' }])
      setEvidenceFiles([])
      isManualEditRef.current = false
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || error.response?.data?.message || 'Gagal mencatat barang terpasang',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Input Barang Terpasang</h1>
          <p className="mt-2 text-sm text-gray-600">Masukkan data barang yang telah terpasang</p>
        </div>
        <button
          type="button"
          onClick={() => navigate('/inventory/installed')}
          className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          Daftar Barang Terpasang
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-4 sm:p-6 space-y-6">
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

        {/* Nomor Barang Keluar - Multiple rows (opsional) */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Nomor Barang Keluar (Opsional)
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
                      >
                        <option value="">
                          {loadingStockOuts 
                            ? 'Memuat data...' 
                            : !formData.mandor_id 
                              ? 'Pilih Mandor terlebih dahulu'
                              : stockOuts.length === 0
                                ? 'Tidak ada data barang keluar untuk mandor ini'
                                : 'Pilih Nomor Barang Keluar (opsional)'}
                        </option>
                        {stockOuts.map((stockOut) => (
                          <option key={stockOut.id} value={stockOut.nomor_barang_keluar}>
                            {formatInstalledStockOutOption(stockOut as any)}
                          </option>
                        ))}
                      </select>
                      {selectedStockOut && (() => {
                        const sisa = getSisaPasang(selectedStockOut as any)
                        const tanggalDisplay = (() => {
                          try {
                            return new Date(formData.tanggal_pasang).toLocaleDateString('id-ID')
                          } catch (_) {
                            return formData.tanggal_pasang
                          }
                        })()
                        return (
                          <p className="mt-2 text-xs text-blue-700">
                            Material: <strong>{selectedStockOut.material?.nama_barang || `ID: ${selectedStockOut.material_id}`}</strong>
                            {' | '}Mandor: <strong>{selectedStockOut.mandor?.nama || `ID: ${selectedStockOut.mandor_id}`}</strong>
                            {' | '}Sisa bisa dipasang: <strong>{sisa !== undefined ? formatDecimal(sisa) : '-'}</strong>
                            {' | '}Tanggal: <strong>{tanggalDisplay}</strong>
                          </p>
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

        {/* Items (Material + Quantity) */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Barang Terpasang <span className="text-red-500">*</span>
            </label>
            {/* <button
              type="button"
              onClick={() => {
                isManualEditRef.current = true
                setItems([...items, { material_id: '', quantity: '' }])
              }}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Tambah Baris
            </button> */}
          </div>

          <div className="overflow-x-auto">
            <div className="min-w-[600px] grid grid-cols-12 gap-3">
              <div className="col-span-7 text-xs font-semibold text-gray-600">Material</div>
              <div className="col-span-4 text-xs font-semibold text-gray-600">Quantity</div>
              <div className="col-span-1" />

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
                
                return (
                <div key={`row-${idx}`} className="contents">
                  <div className="col-span-7">
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
                            {material.kode_barang ? `${material.kode_barang} - ` : ''}{material.nama_barang}
                          </option>
                        ))}
                    </select>
                  </div>
                  <div className="col-span-4">
                    {(() => {
                      const sisaPasang = isAutoFilled && matchingStockOut ? getSisaPasang(matchingStockOut as any) : undefined
                      const isSisaPasangZero = sisaPasang !== undefined && sisaPasang <= 0
                      const isInputDisabled = isAutoFilled && isSisaPasangZero
                      
                      return (
                        <>
                          <input
                            type="number"
                            step="0.01"
                            min="0.01"
                            max={matchingStockOut ? getInstalledMaxQty(matchingStockOut as any) : undefined}
                            value={row.quantity}
                            onChange={(e) => {
                              const v = e.target.value
                              isManualEditRef.current = true
                              setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, quantity: v } : it)))
                            }}
                            disabled={isInputDisabled}
                            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                              isAutoFilled ? 'border-blue-300 bg-blue-50' : 'border-gray-300'
                            } ${isInputDisabled ? 'opacity-50 cursor-not-allowed bg-gray-100' : ''}`}
                            placeholder="Qty"
                            title={(() => {
                              if (isInputDisabled) return 'Sisa bisa dipasang sudah 0, tidak bisa menambah quantity'
                              if (!isAutoFilled || !matchingStockOut) return ''
                              const maxQty = getInstalledMaxQty(matchingStockOut as any)
                              return maxQty !== undefined ? `Maksimal: ${maxQty} (sisa barang kembali yang bisa dipasang)` : ''
                            })()}
                          />
                          {isAutoFilled && matchingStockOut && (() => {
                            const maxQty = getSisaPasang(matchingStockOut as any)
                            if (maxQty === undefined) return null
                            return (
                              <p className={`mt-1 text-xs ${maxQty <= 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                                Sisa bisa dipasang: <strong>{formatDecimal(maxQty)}</strong>
                              </p>
                            )
                          })()}
                        </>
                      )
                    })()}
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

        {/* Tanggal Pasang */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tanggal Pasang <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={formData.tanggal_pasang}
            onChange={(e) => setFormData({ ...formData, tanggal_pasang: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        {/* No Register */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            No Register
          </label>
          <input
            type="text"
            value={formData.no_register}
            onChange={(e) => setFormData({ ...formData, no_register: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Masukkan nomor register (opsional)"
            maxLength={255}
          />
        </div>

        {/* Evidence Upload */}
        <div>
          <EvidenceUpload
            files={evidenceFiles}
            onChange={setEvidenceFiles}
            maxFiles={5}
            maxSize={5}
            label="Upload Evidence (Opsional)"
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
            disabled={(() => {
              // Cek apakah ada item dengan sisa bisa dipasang = 0
              const selectedStockOutNumbers = stockOutRows
                .map(r => r.nomor_barang_keluar)
                .filter(nomor => nomor !== '')
              
              const hasSisaPasangZero = items.some(row => {
                if (!row.material_id) return false
                const matchingStockOut = stockOuts.find(so => 
                  so.material_id?.toString() === row.material_id &&
                  selectedStockOutNumbers.includes(so.nomor_barang_keluar)
                )
                if (!matchingStockOut) return false
                const sisaPasang = getSisaPasang(matchingStockOut as any)
                return sisaPasang !== undefined && sisaPasang <= 0
              })
              
              return loading || hasSisaPasangZero
            })()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={(() => {
              const selectedStockOutNumbers = stockOutRows
                .map(r => r.nomor_barang_keluar)
                .filter(nomor => nomor !== '')
              
              const hasSisaPasangZero = items.some(row => {
                if (!row.material_id) return false
                const matchingStockOut = stockOuts.find(so => 
                  so.material_id?.toString() === row.material_id &&
                  selectedStockOutNumbers.includes(so.nomor_barang_keluar)
                )
                if (!matchingStockOut) return false
                const sisaPasang = getSisaPasang(matchingStockOut as any)
                return sisaPasang !== undefined && sisaPasang <= 0
              })
              
              return hasSisaPasangZero ? 'Tidak bisa menyimpan karena ada item dengan sisa bisa dipasang = 0' : ''
            })()}
          >
            {loading ? 'Menyimpan...' : 'Simpan'}
          </button>
        </div>
      </form>
    </div>
  )
}

