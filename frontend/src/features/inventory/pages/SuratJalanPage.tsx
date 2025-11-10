import { useState, useEffect, useRef } from 'react'
import { getTodayDate } from '@/utils/helpers'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'
import Swal from 'sweetalert2'
import { useNavigate } from 'react-router-dom'
import {
  generateSuratJalanPDF,
  printSuratJalanPDF,
  type SuratJalanData
} from '@/utils/pdfGenerator'
import { inventoryService, SuratJalanCreateRequest, Material, StockOut } from '../services/inventoryService'
import MaterialSelector from '../components/MaterialSelector'

interface FormItem {
  namaBarang: string
  materialId: number | null
  qty: string
  keterangan: string
}

const createEmptyItem = (): FormItem => ({
  namaBarang: '',
  materialId: null,
  qty: '',
  keterangan: ''
})

export default function SuratJalanPage() {
  const navigate = useNavigate()
  const [kepada, setKepada] = useState('')
  const [tanggalPengiriman, setTanggalPengiriman] = useState(getTodayDate())
  const [items, setItems] = useState<FormItem[]>([createEmptyItem()])
  const [namaPemberi, setNamaPemberi] = useState('')
  const [namaPenerima, setNamaPenerima] = useState('')
  const [tanggalDiterima, setTanggalDiterima] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [materials, setMaterials] = useState<Material[]>([])
  const [loadingMaterials, setLoadingMaterials] = useState(false)
  
  // State untuk dropdown No. Barang Keluar
  const [stockOutNumbers, setStockOutNumbers] = useState<string[]>([])
  const [selectedNomorBarangKeluar, setSelectedNomorBarangKeluar] = useState('')
  const [isStockOutDropdownOpen, setIsStockOutDropdownOpen] = useState(false)
  const [searchStockOutTerm, setSearchStockOutTerm] = useState('')
  const [loadingStockOutNumbers, setLoadingStockOutNumbers] = useState(false)
  const stockOutDropdownRef = useRef<HTMLDivElement>(null)
  
  // State untuk dropdown No. Surat Permintaan
  const [suratPermintaanNumbers, setSuratPermintaanNumbers] = useState<string[]>([])
  const [selectedNomorSuratPermintaan, setSelectedNomorSuratPermintaan] = useState('')
  const [isSuratPermintaanDropdownOpen, setIsSuratPermintaanDropdownOpen] = useState(false)
  const [searchSuratPermintaanTerm, setSearchSuratPermintaanTerm] = useState('')
  const [loadingSuratPermintaanNumbers, setLoadingSuratPermintaanNumbers] = useState(false)
  const suratPermintaanDropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadMaterials()
    loadStockOutNumbers()
    loadSuratPermintaanNumbers()
  }, [])

  const loadMaterials = async () => {
    try {
      setLoadingMaterials(true)
      console.log('Loading materials...')
      
      const response = await inventoryService.getMaterials(1, 1000)
      console.log('Raw response from getMaterials:', response)
      console.log('Response type:', typeof response)
      console.log('Is array?', Array.isArray(response))
      console.log('Response keys:', response ? Object.keys(response) : 'null/undefined')
      
      let items: Material[] = []
      
      // Handle different response structures
      if (Array.isArray(response)) {
        // Response langsung array
        items = response as Material[]
        console.log('Response is direct array')
      } else if (response && typeof response === 'object') {
        // Response adalah object, cek berbagai kemungkinan property
        if (Array.isArray((response as any).data)) {
          items = (response as any).data as Material[]
          console.log('Found materials in response.data')
        } else if (Array.isArray((response as any).items)) {
          items = (response as any).items as Material[]
          console.log('Found materials in response.items')
        } else if (Array.isArray((response as any).data?.items)) {
          items = (response as any).data.items as Material[]
          console.log('Found materials in response.data.items')
        } else if (Array.isArray((response as any).data?.data)) {
          items = (response as any).data.data as Material[]
          console.log('Found materials in response.data.data')
        } else {
          console.warn('Could not find materials array in response structure')
          console.warn('Response structure:', JSON.stringify(response, null, 2))
        }
      }
      
      console.log('Final materials count:', items.length)
      if (items.length > 0) {
        console.log('Sample material:', items[0])
        console.log('Active materials:', items.filter(m => m.is_active === 1).length)
      } else {
        console.warn('No materials extracted from response')
      }
      
      setMaterials(items as Material[])
      
      if (items.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Tidak ada data material yang ditemukan. Pastikan sudah ada data material di database.',
          timer: 3000,
        })
      }
    } catch (error: any) {
      console.error('Error loading materials:', error)
      console.error('Error response:', error?.response)
      console.error('Error details:', error?.response?.data || error?.message)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error?.response?.data?.message || error?.response?.data?.detail || error?.message || 'Gagal memuat data materials',
      })
    } finally {
      setLoadingMaterials(false)
    }
  }

  const loadStockOutNumbers = async () => {
    try {
      setLoadingStockOutNumbers(true)
      const numbers = await inventoryService.getUniqueStockOutNumbers()
      setStockOutNumbers(numbers)
    } catch (error: any) {
      console.error('Error loading stock out numbers:', error)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error?.response?.data?.message || error?.response?.data?.detail || error?.message || 'Gagal memuat data nomor barang keluar',
      })
    } finally {
      setLoadingStockOutNumbers(false)
    }
  }

  const loadSuratPermintaanNumbers = async () => {
    try {
      setLoadingSuratPermintaanNumbers(true)
      const response = await inventoryService.getSuratPermintaans(1, 1000)
      const items = response?.data?.items || response?.items || []
      const numbers = items.map((item: any) => item.nomor_surat).filter(Boolean)
      setSuratPermintaanNumbers(numbers)
    } catch (error: any) {
      console.error('Error loading surat permintaan numbers:', error)
      // Tidak perlu show error, karena ini opsional
    } finally {
      setLoadingSuratPermintaanNumbers(false)
    }
  }

  const handleSelectNomorBarangKeluar = async (nomor: string) => {
    if (!nomor) {
      setSelectedNomorBarangKeluar('')
      return
    }

    try {
      setLoadingStockOutNumbers(true)
      const response = await inventoryService.getStockOutByNomor(nomor)
      const stockOuts = Array.isArray(response?.data) ? response.data : (Array.isArray(response) ? response : [])
      
      if (stockOuts.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Tidak ada data barang keluar untuk nomor tersebut',
        })
        setSelectedNomorBarangKeluar('')
        return
      }

      // Map stock out ke format FormItem
      const mappedItems: FormItem[] = stockOuts.map((stockOut: StockOut) => {
        const material = stockOut.material
        return {
          namaBarang: material?.nama_barang || '',
          materialId: material?.id || null,
          qty: stockOut.quantity?.toString() || '0',
          keterangan: ''
        }
      })

      if (mappedItems.length > 0) {
        setItems(mappedItems)
        setSelectedNomorBarangKeluar(nomor)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: `Data berhasil dimuat dari nomor barang keluar ${nomor}`,
          timer: 1500,
          showConfirmButton: false
        })
      } else {
        setSelectedNomorBarangKeluar('')
      }
    } catch (error: any) {
      console.error('Error loading stock out by nomor:', error)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error?.response?.data?.message || error?.response?.data?.detail || error?.message || 'Gagal memuat detail barang keluar',
      })
      setSelectedNomorBarangKeluar('')
    } finally {
      setLoadingStockOutNumbers(false)
    }
  }

  // Handle click outside untuk dropdown stock out
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (stockOutDropdownRef.current && !stockOutDropdownRef.current.contains(event.target as Node)) {
        setIsStockOutDropdownOpen(false)
        setSearchStockOutTerm('')
      }
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

  // Filter stock out numbers berdasarkan search term
  const filteredStockOutNumbers = stockOutNumbers.filter((nomor) =>
    nomor.toLowerCase().includes(searchStockOutTerm.toLowerCase())
  )

  // Filter surat permintaan numbers berdasarkan search term
  const filteredSuratPermintaanNumbers = suratPermintaanNumbers.filter((nomor) =>
    nomor.toLowerCase().includes(searchSuratPermintaanTerm.toLowerCase())
  )

  const handleItemChange = (index: number, field: keyof FormItem, value: string) => {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    )
  }

  const handleMaterialSelect = (index: number, material: Material | null) => {
    setItems((prev) =>
      prev.map((item, i) => {
        if (i === index) {
          if (material) {
            return {
              ...item,
              materialId: material.id,
              namaBarang: material.nama_barang
            }
          } else {
            return {
              ...item,
              materialId: null,
              namaBarang: ''
            }
          }
        }
        return item
      })
    )
  }

  const handleMaterialManualChange = (index: number, value: string) => {
    // Tidak mengizinkan input manual yang tidak valid
    // Jika user menghapus semua text, reset materialId
    if (!value.trim()) {
      setItems((prev) =>
        prev.map((item, i) => 
          i === index ? { ...item, materialId: null, namaBarang: '' } : item
        )
      )
    } else {
      // Jika user mengetik manual, cek apakah ada material yang cocok
      // Jika tidak ada yang cocok, tetap set materialId null untuk memaksa user pilih dari dropdown
      const matchedMaterial = materials.find(m => 
        m.is_active === 1 && 
        (m.nama_barang.toLowerCase() === value.toLowerCase() || 
         (m.kode_barang && m.kode_barang.toLowerCase() === value.toLowerCase()))
      )
      
      if (!matchedMaterial) {
        // Jika tidak ada yang cocok, reset materialId tapi biarkan namaBarang untuk search
        setItems((prev) =>
          prev.map((item, i) => 
            i === index ? { ...item, materialId: null, namaBarang: value } : item
          )
        )
      }
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

  const handleExportPDF = async () => {
    try {
      // Validasi minimal
      if (!kepada.trim()) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Kepada tidak boleh kosong',
        })
        return
      }

      if (items.length === 0 || items.some(item => !item.namaBarang.trim() || !item.materialId)) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Semua item harus memilih barang dari database',
        })
        return
      }

      const pdfData: SuratJalanData = {
        nomorForm: 'AUTO-GENERATED', // Akan digenerate oleh backend
        kepada,
        tanggalPengiriman,
        items: items.map((item, index) => ({
          no: index + 1,
          namaBarang: item.namaBarang,
          qty: parseFloat(item.qty) || 0,
          ket: item.keterangan
        })),
        namaPemberi: namaPemberi || undefined,
        namaPenerima: namaPenerima || undefined,
        tanggalDiterima: tanggalDiterima || undefined
      }

      await generateSuratJalanPDF(pdfData)
      
      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'PDF berhasil di-generate',
        timer: 1500,
        showConfirmButton: false
      })
    } catch (error: any) {
      await Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error.message || 'Gagal generate PDF'
      })
    }
  }

  const handlePrintPDF = async () => {
    try {
      // Validasi minimal
      if (!kepada.trim()) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Kepada tidak boleh kosong',
        })
        return
      }

      if (items.length === 0 || items.some(item => !item.namaBarang.trim() || !item.materialId)) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Semua item harus memilih barang dari database',
        })
        return
      }

      const pdfData: SuratJalanData = {
        nomorForm: 'AUTO-GENERATED',
        kepada,
        tanggalPengiriman,
        items: items.map((item, index) => ({
          no: index + 1,
          namaBarang: item.namaBarang,
          qty: parseFloat(item.qty) || 0,
          ket: item.keterangan
        })),
        namaPemberi: namaPemberi || undefined,
        namaPenerima: namaPenerima || undefined,
        tanggalDiterima: tanggalDiterima || undefined
      }

      await printSuratJalanPDF(pdfData)
    } catch (error: any) {
      await Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error.message || 'Gagal print PDF'
      })
    }
  }

  const handleSubmit = async () => {
    // Validasi form
    if (!kepada.trim()) {
      await Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Kepada tidak boleh kosong',
      })
      return
    }

    if (!tanggalPengiriman) {
      await Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Tanggal pengiriman tidak boleh kosong',
      })
      return
    }

    if (items.length === 0) {
      await Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Minimal harus ada 1 item barang',
      })
      return
    }

    // Validasi setiap item
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (!item.materialId || !item.namaBarang.trim()) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Item ke-${i + 1}: Harus memilih barang dari database`,
        })
        return
      }
      if (!item.qty || parseFloat(item.qty) <= 0) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: `Item ke-${i + 1}: Qty harus lebih dari 0`,
        })
        return
      }
    }

    setIsSubmitting(true)

    try {
      const requestData: SuratJalanCreateRequest = {
        kepada: kepada.trim(),
        tanggal_pengiriman: tanggalPengiriman,
        items: items.map((item) => ({
          nama_barang: item.namaBarang.trim(),
          qty: parseFloat(item.qty) || 0,
          keterangan: item.keterangan.trim() || undefined
        })),
        nama_pemberi: namaPemberi.trim() || undefined,
        nama_penerima: namaPenerima.trim() || undefined,
        tanggal_diterima: tanggalDiterima || undefined,
        nomor_surat_permintaan: selectedNomorSuratPermintaan || undefined,
        nomor_barang_keluar: selectedNomorBarangKeluar || undefined
      }

      const response = await inventoryService.createSuratJalan(requestData)
      
      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Surat Jalan berhasil dibuat',
        timer: 2000,
        showConfirmButton: false
      })

      // Navigate to list page
      navigate('/inventory/surat-jalan/list')
    } catch (error: any) {
      await Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error.response?.data?.message || error.message || 'Gagal membuat surat jalan'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 lg:p-8">
        {/* Header */}
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
            <div className="flex items-center gap-3 mb-4 sm:mb-0">
              <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">K</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">PT Kian Santang Muliatama Tbk</h1>
                <p className="text-lg font-bold text-slate-800 mt-1">DELIVERY SLIP</p>
              </div>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <Input
                label="KEPADA"
                type="text"
                value={kepada}
                onChange={(e) => setKepada(e.target.value)}
                placeholder="Masukkan nama penerima"
                required
              />
            </div>
            <div>
              <Input
                label="Tanggal Pengiriman"
                type="date"
                value={tanggalPengiriman}
                onChange={(e) => setTanggalPengiriman(e.target.value)}
                required
              />
            </div>
          </div>
        </div>

        {/* Table Section */}
        <div className="mb-6">
          {/* Dropdown Search No. Surat Permintaan */}
          <div className="mb-4 relative hidden" ref={suratPermintaanDropdownRef}>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pilih No. Surat Permintaan (Opsional)
            </label>
            <div className="relative">
              <input
                type="text"
                value={isSuratPermintaanDropdownOpen ? searchSuratPermintaanTerm : (selectedNomorSuratPermintaan || '')}
                onChange={(e) => {
                  setSearchSuratPermintaanTerm(e.target.value)
                  if (!isSuratPermintaanDropdownOpen) setIsSuratPermintaanDropdownOpen(true)
                }}
                onFocus={() => {
                  setIsSuratPermintaanDropdownOpen(true)
                  if (!searchSuratPermintaanTerm && selectedNomorSuratPermintaan) {
                    setSearchSuratPermintaanTerm(selectedNomorSuratPermintaan)
                  }
                }}
                onBlur={() => {
                  setTimeout(() => {
                    if (suratPermintaanDropdownRef.current && !suratPermintaanDropdownRef.current.contains(document.activeElement)) {
                      setIsSuratPermintaanDropdownOpen(false)
                      if (!selectedNomorSuratPermintaan) {
                        setSearchSuratPermintaanTerm('')
                      }
                    }
                  }, 200)
                }}
                placeholder={loadingSuratPermintaanNumbers ? "Memuat data..." : "Cari atau pilih nomor surat permintaan..."}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 pr-10"
                disabled={loadingSuratPermintaanNumbers}
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                {loadingSuratPermintaanNumbers ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-500"></div>
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

            {isSuratPermintaanDropdownOpen && !loadingSuratPermintaanNumbers && (
              <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
                {filteredSuratPermintaanNumbers.length === 0 ? (
                  <div className="px-4 py-2 text-sm text-gray-500 text-center">
                    {searchSuratPermintaanTerm ? 'Tidak ada nomor yang cocok' : 'Tidak ada data nomor surat permintaan'}
                  </div>
                ) : (
                  <ul className="py-1">
                    {filteredSuratPermintaanNumbers.map((nomor) => (
                      <li
                        key={nomor}
                        onClick={() => {
                          setSelectedNomorSuratPermintaan(nomor)
                          setSearchSuratPermintaanTerm('')
                          setIsSuratPermintaanDropdownOpen(false)
                        }}
                        className={`px-4 py-2 text-sm cursor-pointer hover:bg-indigo-50 ${
                          selectedNomorSuratPermintaan === nomor ? 'bg-indigo-100 font-medium' : ''
                        }`}
                      >
                        {nomor}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>

          {/* Dropdown Search No. Barang Keluar */}
          <div className="mb-4 relative" ref={stockOutDropdownRef}>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pilih No. Barang Keluar (Opsional)
            </label>
            <div className="relative">
              <input
                type="text"
                value={isStockOutDropdownOpen ? searchStockOutTerm : (selectedNomorBarangKeluar || '')}
                onChange={(e) => {
                  setSearchStockOutTerm(e.target.value)
                  if (!isStockOutDropdownOpen) setIsStockOutDropdownOpen(true)
                }}
                onFocus={() => {
                  setIsStockOutDropdownOpen(true)
                  if (!searchStockOutTerm && selectedNomorBarangKeluar) {
                    setSearchStockOutTerm(selectedNomorBarangKeluar)
                  }
                }}
                onBlur={() => {
                  setTimeout(() => {
                    if (stockOutDropdownRef.current && !stockOutDropdownRef.current.contains(document.activeElement)) {
                      setIsStockOutDropdownOpen(false)
                      if (!selectedNomorBarangKeluar) {
                        setSearchStockOutTerm('')
                      }
                    }
                  }, 200)
                }}
                placeholder={loadingStockOutNumbers ? "Memuat data..." : "Cari atau pilih nomor barang keluar..."}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 pr-10"
                disabled={loadingStockOutNumbers}
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                {loadingStockOutNumbers ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-amber-500"></div>
                ) : (
                  <svg
                    className={`h-5 w-5 text-gray-400 transition-transform ${isStockOutDropdownOpen ? 'transform rotate-180' : ''}`}
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

            {isStockOutDropdownOpen && !loadingStockOutNumbers && (
              <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
                {filteredStockOutNumbers.length === 0 ? (
                  <div className="px-4 py-2 text-sm text-gray-500 text-center">
                    {searchStockOutTerm ? 'Tidak ada nomor yang cocok' : 'Tidak ada data nomor barang keluar'}
                  </div>
                ) : (
                  filteredStockOutNumbers.map((nomor) => (
                    <div
                      key={nomor}
                      onClick={() => {
                        handleSelectNomorBarangKeluar(nomor)
                        setIsStockOutDropdownOpen(false)
                        setSearchStockOutTerm('')
                      }}
                      className={`px-4 py-2 text-sm cursor-pointer hover:bg-amber-50 ${
                        selectedNomorBarangKeluar === nomor ? 'bg-amber-100 font-semibold' : ''
                      }`}
                    >
                      {nomor}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold text-slate-900">Daftar Barang</h3>
            <Button
              variant="primary"
              size="sm"
              onClick={handleTambahBarang}
              className="flex items-center gap-2"
            >
              <span>+</span>
              <span className="hidden sm:inline">Tambah Barang</span>
            </Button>
          </div>
          <div className="overflow-x-auto" style={{ position: 'relative' }}>
            <table className="w-full border-collapse border border-slate-300 text-sm">
              <thead>
                <tr className="bg-slate-50">
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">NO</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">NAMA BARANG</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">QTY</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">KET</th>
                  <th className="border border-slate-300 px-2 py-2 text-center font-semibold">AKSI</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => (
                  <tr key={index} className="hover:bg-slate-50">
                    <td className="border border-slate-300 px-2 py-2 text-center">{index + 1}</td>
                    <td className="border border-slate-300 px-2 py-1 relative" style={{ overflow: 'visible' }}>
                      <div className="w-full border border-slate-300 rounded focus-within:ring-2 focus-within:ring-amber-500">
                        {loadingMaterials ? (
                          <div className="px-2 py-1 text-sm text-slate-500">Memuat data...</div>
                        ) : materials.length === 0 ? (
                          <div className="px-2 py-1 text-sm text-red-500">
                            Tidak ada data material. Silakan refresh halaman.
                          </div>
                        ) : (
                          <MaterialSelector
                            value={item.namaBarang}
                            materials={materials}
                            onSelect={(material) => handleMaterialSelect(index, material)}
                            onManualChange={(value) => handleMaterialManualChange(index, value)}
                            placeholder="Pilih atau ketik nama barang..."
                            disabled={false}
                          />
                        )}
                      </div>
                    </td>
                    <td className="border border-slate-300 px-2 py-1">
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={item.qty}
                        onChange={(e) => handleItemChange(index, 'qty', e.target.value)}
                        className="w-full px-2 py-1 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-amber-500"
                        placeholder="0"
                        required
                      />
                    </td>
                    <td className="border border-slate-300 px-2 py-1">
                      <input
                        type="text"
                        value={item.keterangan}
                        onChange={(e) => handleItemChange(index, 'keterangan', e.target.value)}
                        className="w-full px-2 py-1 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-amber-500"
                        placeholder="Keterangan (opsional)"
                      />
                    </td>
                    <td className="border border-slate-300 px-2 py-2 text-center">
                      <button
                        onClick={() => handleHapusBarang(index)}
                        className="text-red-600 hover:text-red-800 font-semibold"
                        disabled={items.length === 1}
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

        {/* Footer Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Left - Pemberi */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Pemberi</h3>
            <Input
              label="Nama Pemberi"
              type="text"
              value={namaPemberi}
              onChange={(e) => setNamaPemberi(e.target.value)}
              placeholder="Masukkan nama pemberi (opsional)"
            />
          </div>

          {/* Right - Penerima */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Penerima</h3>
            <Input
              label="Tanggal Diterima"
              type="date"
              value={tanggalDiterima}
              onChange={(e) => setTanggalDiterima(e.target.value)}
              placeholder="Tanggal diterima (opsional)"
            />
            <Input
              label="Nama Penerima"
              type="text"
              value={namaPenerima}
              onChange={(e) => setNamaPenerima(e.target.value)}
              placeholder="Masukkan nama penerima (opsional)"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-end pt-4 border-t border-slate-200">
          <Button
            variant="secondary"
            onClick={() => navigate('/inventory/surat-jalan/list')}
            disabled={isSubmitting}
            className="hidden"
          >
            Batal
          </Button>
          <Button
            variant="secondary"
            onClick={handleExportPDF}
            disabled={isSubmitting}
            className="hidden"
          >
            Export PDF
          </Button>
          <Button
            variant="secondary"
            onClick={handlePrintPDF}
            disabled={isSubmitting}
            className="hidden"
          >
            Print PDF
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Menyimpan...' : 'Simpan'}
          </Button>
        </div>
      </div>
    </div>
  )
}

