import { useState, useEffect } from 'react'
import { getTodayDate, formatDecimal } from '@/utils/helpers'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'
import Swal from 'sweetalert2'
import {
  generateSuratPermintaanPDF,
  printSuratPermintaanPDF,
  type SuratPermintaanData
} from '@/utils/pdfGenerator'
import { inventoryService, Material, SuratPermintaanCreateRequest } from '../services/inventoryService'
import MaterialSelector from '../components/MaterialSelector'
import { useAppSelector } from '@/store/hooks'

interface FormItem {
  kodeBarang: string
  namaBarang: string
  qty: string
  sat: string
  materialId: number | null // Track material ID yang dipilih
  sumberBarang: {
    proyek: boolean
    proyekValue: string
    stok: boolean
    stokValue: string
  }
  peruntukan: {
    proyek: boolean
    proyekValue: string
    produksi: boolean
    produksiValue: string
    kantor: boolean
    lainLain: boolean
  }
}

interface SignatureData {
  pemohon: string
  menyetujui: string
  yangMenyerahkan: string
  mengetahuiSPV: string
  mengetahuiAdminGudang: string
}

const createEmptyItem = (): FormItem => ({
  kodeBarang: '',
  namaBarang: '',
  qty: '',
  sat: '',
  materialId: null,
  sumberBarang: {
    proyek: false,
    proyekValue: '',
    stok: false,
    stokValue: ''
  },
  peruntukan: {
    proyek: false,
    proyekValue: '',
    produksi: false,
    produksiValue: '',
    kantor: false,
    lainLain: false
  }
})

export default function SuratPermintaanPage() {
  const { currentProject } = useAppSelector((state) => state.project)
  const [tanggal, setTanggal] = useState(getTodayDate())
  const [items, setItems] = useState<FormItem[]>([createEmptyItem()])
  const [materials, setMaterials] = useState<Material[]>([])
  const [materialStocks, setMaterialStocks] = useState<{ [key: number]: number }>({})
  const [signatures, setSignatures] = useState<SignatureData>({
    pemohon: '',
    menyetujui: '',
    yangMenyerahkan: '',
    mengetahuiSPV: '',
    mengetahuiAdminGudang: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

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
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Gagal memuat data materials',
      })
    }
  }

  // Ambil stok saat ini ketika material berubah di items
  useEffect(() => {
    const fetchStocks = async () => {
      const materialIds = items
        .map((item) => item.materialId)
        .filter((id) => id !== null && id !== undefined) as number[]

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
          const raw = ((res as any)?.data?.data ?? (res as any)?.data ?? res) as any
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

  const handleItemChange = (index: number, field: keyof FormItem, value: any) => {
    setItems((prev) =>
      prev.map((item, i) => {
        if (i === index) {
          const updated = { ...item, [field]: value }
          // Jika user input manual kodeBarang atau namaBarang, clear materialId
          if ((field === 'kodeBarang' || field === 'namaBarang') && item.materialId !== null) {
            updated.materialId = null
          }
          return updated
        }
        return item
      })
    )
  }

  const handleMaterialSelect = (index: number, material: Material | null) => {
    if (material) {
      setItems((prev) =>
        prev.map((item, i) =>
          i === index
            ? {
                ...item,
                kodeBarang: material.kode_barang || '',
                namaBarang: material.nama_barang,
                sat: material.satuan,
                materialId: material.id
              }
            : item
        )
      )
    } else {
      // Clear material selection
      setItems((prev) =>
        prev.map((item, i) =>
          i === index ? { ...item, materialId: null } : item
        )
      )
    }
  }

  const handleMaterialManualChange = (index: number, value: string) => {
    // User sedang mengetik manual, clear materialId
    setItems((prev) =>
      prev.map((item, i) =>
        i === index
          ? {
              ...item,
              kodeBarang: value,
              materialId: null
            }
          : item
      )
    )
  }

  const handleSumberBarangChange = (
    index: number,
    field: 'proyek' | 'stok' | 'proyekValue' | 'stokValue',
    value: any
  ) => {
    setItems((prev) =>
      prev.map((item, i) => {
        if (i === index) {
          const newSumberBarang = { ...item.sumberBarang }
          if (field === 'proyek') {
            newSumberBarang.proyek = value
            if (value) {
              // Auto-fill nama proyek dari currentProject saat checkbox dicentang
              newSumberBarang.proyekValue = currentProject?.name || ''
            } else {
              // Jika proyek di-uncheck, clear value
              newSumberBarang.proyekValue = ''
            }
          } else if (field === 'stok') {
            newSumberBarang.stok = value
            if (value) {
              // Auto-fill stok value dengan jumlah stok yang sama dengan info stok
              const materialId = item.materialId
              if (materialId !== null && materialStocks[materialId] !== undefined) {
                newSumberBarang.stokValue = materialStocks[materialId].toString()
              } else {
                newSumberBarang.stokValue = ''
              }
            } else {
              // Jika stok di-uncheck, clear value
              newSumberBarang.stokValue = ''
            }
          } else if (field === 'proyekValue') {
            newSumberBarang.proyekValue = value
          } else if (field === 'stokValue') {
            newSumberBarang.stokValue = value
          }
          return { ...item, sumberBarang: newSumberBarang }
        }
        return item
      })
    )
  }

  const handlePeruntukanChange = (
    index: number,
    field: 'proyek' | 'produksi' | 'kantor' | 'lainLain' | 'proyekValue' | 'produksiValue',
    value: any
  ) => {
    setItems((prev) =>
      prev.map((item, i) => {
        if (i === index) {
          const newPeruntukan = { ...item.peruntukan }
          if (field === 'proyek') {
            newPeruntukan.proyek = value
            if (value) {
              // Auto-fill nama proyek dari currentProject saat checkbox dicentang
              newPeruntukan.proyekValue = currentProject?.name || ''
            } else {
              newPeruntukan.proyekValue = ''
            }
          } else if (field === 'produksi') {
            newPeruntukan.produksi = value
            if (!value) {
              newPeruntukan.produksiValue = ''
            }
          } else if (field === 'kantor') {
            newPeruntukan.kantor = value
          } else if (field === 'lainLain') {
            newPeruntukan.lainLain = value
          } else if (field === 'proyekValue') {
            newPeruntukan.proyekValue = value
          } else if (field === 'produksiValue') {
            newPeruntukan.produksiValue = value
          }
          return { ...item, peruntukan: newPeruntukan }
        }
        return item
      })
    )
  }

  const handleExportPDF = async () => {
    try {
      const pdfData: SuratPermintaanData = {
        tanggal,
        items: items.map((item, index) => ({
          no: index + 1,
          kodeBarang: item.kodeBarang,
          namaBarang: item.namaBarang,
          qty: item.qty,
          sat: item.sat,
          sumberBarang: item.sumberBarang,
          peruntukan: item.peruntukan
        })),
        signatures
      }

      await generateSuratPermintaanPDF(pdfData)
      
      Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'PDF berhasil di-generate',
        timer: 1500,
        showConfirmButton: false
      })
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error.message || 'Gagal generate PDF'
      })
    }
  }

  const handlePrintPDF = async () => {
    try {
      const pdfData: SuratPermintaanData = {
        tanggal,
        items: items.map((item, index) => ({
          no: index + 1,
          kodeBarang: item.kodeBarang,
          namaBarang: item.namaBarang,
          qty: item.qty,
          sat: item.sat,
          sumberBarang: item.sumberBarang,
          peruntukan: item.peruntukan
        })),
        signatures
      }

      await printSuratPermintaanPDF(pdfData)
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error.message || 'Gagal print PDF'
      })
    }
  }

  const handleSubmit = async () => {
    // Validasi form
    if (!tanggal) {
      await Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Tanggal harus diisi'
      })
      return
    }

    if (items.length === 0) {
      await Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Minimal harus ada 1 item barang'
      })
      return
    }

    // Validasi setiap item
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (!item.namaBarang || !item.namaBarang.trim()) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Nama barang pada item ke-${i + 1} harus diisi`
        })
        return
      }
      if (!item.qty || parseFloat(item.qty) <= 0) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Quantity pada item ke-${i + 1} harus lebih dari 0`
        })
        return
      }
      if (!item.sat || !item.sat.trim()) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Satuan pada item ke-${i + 1} harus diisi`
        })
        return
      }
    }

    if (!currentProject) {
      await Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Project belum dipilih'
      })
      return
    }

    if (!currentProject.code) {
      await Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Project tidak memiliki kode, tidak dapat membuat surat permintaan'
      })
      return
    }

    setIsSubmitting(true)
    
    try {
      // Prepare data untuk submit
      const submitData: SuratPermintaanCreateRequest = {
        tanggal,
        items: items.map((item) => ({
          material_id: item.materialId || null,
          kode_barang: item.kodeBarang || null,
          nama_barang: item.namaBarang,
          qty: parseFloat(item.qty),
          satuan: item.sat,
          sumber_barang: item.sumberBarang,
          peruntukan: item.peruntukan
        })),
        signatures: {
          pemohon: signatures.pemohon || undefined,
          menyetujui: signatures.menyetujui || undefined,
          yangMenyerahkan: signatures.yangMenyerahkan || undefined,
          mengetahuiSPV: signatures.mengetahuiSPV || undefined,
          mengetahuiAdminGudang: signatures.mengetahuiAdminGudang || undefined
        }
      }

      const response = await inventoryService.createSuratPermintaan(submitData)
      const nomorSurat = response?.data?.nomor_surat || 'Surat Permintaan'
      
      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: `Surat permintaan ${nomorSurat} berhasil dibuat`,
        timer: 3000,
        showConfirmButton: true
      })

      // Reset form
      setTanggal(getTodayDate())
      setItems([createEmptyItem()])
      setSignatures({
        pemohon: '',
        menyetujui: '',
        yangMenyerahkan: '',
        mengetahuiSPV: '',
        mengetahuiAdminGudang: ''
      })
    } catch (error: any) {
      console.error('Error submitting surat permintaan:', error)
      await Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error?.response?.data?.message || error?.message || 'Gagal menyimpan surat permintaan'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTambahBarang = () => {
    setItems((prev) => [...prev, createEmptyItem()])
  }

  const handleHapusBarang = (index: number) => {
    if (items.length > 1) {
      setItems((prev) => prev.filter((_, i) => i !== index))
    } else {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Minimal harus ada 1 barang',
        timer: 1500,
        showConfirmButton: false
      })
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8">
        {/* Header */}
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
            <div className="flex items-center gap-3 mb-4 sm:mb-0">
              <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">K</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">PT Kian Santang Muliatama Tbk</h1>
                <p className="text-lg font-bold text-slate-800 mt-1">PERMOHONAN PENGAMBILAN BARANG</p>
              </div>
            </div>
            <div className="text-xs text-slate-600 space-y-1">
              <div>No. Dok: FM-KSM-WH-08</div>
              <div>Revisi: 00</div>
              <div>Tgl Efektif: 28/01/2019</div>
              <div>Halaman: Page 1 of 1</div>
            </div>
          </div>

          {/* Tanggal Input */}
          <div className="mt-4">
            <Input
              label="Tanggal"
              type="date"
              value={tanggal}
              onChange={(e) => setTanggal(e.target.value)}
            />
          </div>
        </div>

        {/* Table Section */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold text-slate-900">Daftar Barang</h3>
            <Button
              variant="primary"
              size="sm"
              onClick={handleTambahBarang}
              className="flex items-center gap-2"
            >
              <span>+</span>
              <span>Tambah Barang</span>
            </Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-slate-300 text-sm">
              <thead>
                <tr className="bg-slate-50">
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">NO.</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">KODE BARANG</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">NAMA BARANG</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">QTY</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">SAT.</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">SUMBER BARANG (Acc.)</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">PERUNTUKAN</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">AKSI</th>
                </tr>
              </thead>
            <tbody>
              {items.map((item, index) => (
                <tr key={index} className="hover:bg-slate-50">
                  <td className="border border-slate-300 px-2 py-2 text-center">{index + 1}</td>
                  <td className="border border-slate-300 px-2 py-1">
                    <MaterialSelector
                      value={item.kodeBarang}
                      materials={materials}
                      onSelect={(material) => handleMaterialSelect(index, material)}
                      onManualChange={(value) => handleMaterialManualChange(index, value)}
                      placeholder="Ketik kode atau nama..."
                    />
                  </td>
                  <td className="border border-slate-300 px-2 py-1">
                    <input
                      type="text"
                      value={item.namaBarang}
                      onChange={(e) => handleItemChange(index, 'namaBarang', e.target.value)}
                      className="w-full px-2 py-1 border-0 focus:outline-none focus:ring-1 focus:ring-indigo-500 rounded"
                      placeholder="Nama Barang"
                      readOnly={item.materialId !== null}
                      style={item.materialId !== null ? { backgroundColor: '#f3f4f6', cursor: 'not-allowed' } : {}}
                      title={item.materialId !== null ? 'Nama barang terisi otomatis dari database' : ''}
                    />
                  </td>
                  <td className="border border-slate-300 px-2 py-1">
                    <div>
                      <input
                        type="number"
                        step="0.01"
                        value={item.qty}
                        onChange={(e) => {
                          const raw = e.target.value
                          const materialId = item.materialId
                          const currentStock = materialId !== null ? materialStocks[materialId] : undefined
                          
                          // Validasi stok jika material dipilih dari database
                          if (materialId !== null && currentStock !== undefined && currentStock !== null) {
                            const parsed = parseFloat(raw)
                            let next = raw
                            if (!isNaN(parsed)) {
                              let clamped = Math.max(0, parsed)
                              clamped = Math.min(clamped, currentStock)
                              next = clamped.toString()
                            } else if (raw === '') {
                              next = ''
                            }
                            handleItemChange(index, 'qty', next)
                          } else {
                            // Input bebas jika manual atau stok tidak tersedia
                            handleItemChange(index, 'qty', raw)
                          }
                        }}
                        className="w-full px-2 py-1 border-0 focus:outline-none focus:ring-1 focus:ring-indigo-500 rounded"
                        placeholder="0"
                        min="0"
                        max={item.materialId !== null && materialStocks[item.materialId] !== undefined 
                          ? materialStocks[item.materialId] 
                          : undefined}
                        disabled={item.materialId !== null && materialStocks[item.materialId] !== undefined && materialStocks[item.materialId] <= 0}
                      />
                      {item.materialId !== null && materialStocks[item.materialId] !== undefined && (
                        <p className={`mt-1 text-xs ${materialStocks[item.materialId] <= 0 ? 'text-red-600' : 'text-green-600'}`}>
                          Stok: <span className="font-semibold">{formatDecimal(materialStocks[item.materialId])}</span> {item.sat || ''}
                        </p>
                      )}
                    </div>
                  </td>
                  <td className="border border-slate-300 px-2 py-1">
                    <input
                      type="text"
                      value={item.sat}
                      onChange={(e) => handleItemChange(index, 'sat', e.target.value)}
                      className="w-full px-2 py-1 border-0 focus:outline-none focus:ring-1 focus:ring-indigo-500 rounded"
                      placeholder="Pcs"
                    />
                  </td>
                  <td className="border border-slate-300 px-2 py-2">
                    <div className="space-y-1">
                      <label className="flex items-center gap-1 text-xs">
                        <input
                          type="checkbox"
                          checked={item.sumberBarang.proyek}
                          onChange={(e) => handleSumberBarangChange(index, 'proyek', e.target.checked)}
                          className="w-3 h-3"
                        />
                        <span>Proyek:</span>
                        {item.sumberBarang.proyek && (
                          <input
                            type="text"
                            value={item.sumberBarang.proyekValue}
                            onChange={(e) => handleSumberBarangChange(index, 'proyekValue', e.target.value)}
                            className="flex-1 px-1 py-0.5 border border-slate-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            placeholder="Nama Proyek"
                          />
                        )}
                      </label>
                      <label className="flex items-center gap-1 text-xs">
                        <input
                          type="checkbox"
                          checked={item.sumberBarang.stok}
                          onChange={(e) => handleSumberBarangChange(index, 'stok', e.target.checked)}
                          className="w-3 h-3"
                        />
                        <span>Stok:</span>
                        {item.sumberBarang.stok && (
                          <input
                            type="text"
                            value={item.sumberBarang.stokValue}
                            onChange={(e) => handleSumberBarangChange(index, 'stokValue', e.target.value)}
                            className="flex-1 px-1 py-0.5 border border-slate-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            placeholder="Detail Stok"
                          />
                        )}
                      </label>
                    </div>
                  </td>
                  <td className="border border-slate-300 px-2 py-2">
                    <div className="space-y-1">
                      <label className="flex items-center gap-1 text-xs">
                        <input
                          type="checkbox"
                          checked={item.peruntukan.proyek}
                          onChange={(e) => handlePeruntukanChange(index, 'proyek', e.target.checked)}
                          className="w-3 h-3"
                        />
                        <span>Proyek:</span>
                        {item.peruntukan.proyek && (
                          <input
                            type="text"
                            value={item.peruntukan.proyekValue}
                            onChange={(e) => handlePeruntukanChange(index, 'proyekValue', e.target.value)}
                            className="flex-1 px-1 py-0.5 border border-slate-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            placeholder="Nama Proyek"
                          />
                        )}
                      </label>
                      <label className="flex items-center gap-1 text-xs">
                        <input
                          type="checkbox"
                          checked={item.peruntukan.produksi}
                          onChange={(e) => handlePeruntukanChange(index, 'produksi', e.target.checked)}
                          className="w-3 h-3"
                        />
                        <span>Produksi:</span>
                        {item.peruntukan.produksi && (
                          <input
                            type="text"
                            value={item.peruntukan.produksiValue}
                            onChange={(e) => handlePeruntukanChange(index, 'produksiValue', e.target.value)}
                            className="flex-1 px-1 py-0.5 border border-slate-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            placeholder="Detail Produksi"
                          />
                        )}
                      </label>
                      <label className="flex items-center gap-1 text-xs">
                        <input
                          type="checkbox"
                          checked={item.peruntukan.kantor}
                          onChange={(e) => handlePeruntukanChange(index, 'kantor', e.target.checked)}
                          className="w-3 h-3"
                        />
                        <span>Kantor</span>
                      </label>
                      <label className="flex items-center gap-1 text-xs">
                        <input
                          type="checkbox"
                          checked={item.peruntukan.lainLain}
                          onChange={(e) => handlePeruntukanChange(index, 'lainLain', e.target.checked)}
                          className="w-3 h-3"
                        />
                        <span>Lain-lain</span>
                      </label>
                    </div>
                  </td>
                  <td className="border border-slate-300 px-2 py-2 text-center">
                    <button
                      type="button"
                      onClick={() => handleHapusBarang(index)}
                      disabled={items.length === 1}
                      className="px-3 py-1.5 text-xs bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Hapus
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>

        {/* Signature Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Tanda Tangan dan Persetujuan</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Pemohon (Mandor)
              </label>
              <Input
                type="text"
                value={signatures.pemohon}
                onChange={(e) => setSignatures({ ...signatures, pemohon: e.target.value })}
                placeholder="Nama Pemohon"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Menyetujui (PIC)
              </label>
              <Input
                type="text"
                value={signatures.menyetujui}
                onChange={(e) => setSignatures({ ...signatures, menyetujui: e.target.value })}
                placeholder="Nama PIC"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Yang Menyerahkan
              </label>
              <Input
                type="text"
                value={signatures.yangMenyerahkan}
                onChange={(e) => setSignatures({ ...signatures, yangMenyerahkan: e.target.value })}
                placeholder="Nama Penyerah"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Mengetahui (SPV)
              </label>
              <Input
                type="text"
                value={signatures.mengetahuiSPV}
                onChange={(e) => setSignatures({ ...signatures, mengetahuiSPV: e.target.value })}
                placeholder="Nama Supervisor"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Mengetahui Admin Gudang
              </label>
              <Input
                type="text"
                value={signatures.mengetahuiAdminGudang}
                onChange={(e) => setSignatures({ ...signatures, mengetahuiAdminGudang: e.target.value })}
                placeholder="Nama Admin"
              />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-end pt-4 border-t border-slate-200">
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="w-full sm:w-auto"
          >
            {isSubmitting ? 'Menyimpan...' : 'Submit'}
          </Button>
        </div>
      </div>
    </div>
  )
}

