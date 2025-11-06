import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { inventoryService, StockIn, Material } from '../services/inventoryService'
import { extractItems } from '@/utils/api'
import Swal from 'sweetalert2'
import DateRangeFilter from '@/components/common/DateRangeFilter'
import { useInventoryList } from '../hooks/useInventoryList'
import { API_BASE_URL } from '@/utils/constants'
import { formatDecimal } from '@/utils/helpers'
import EvidenceUpload from '../components/EvidenceUpload'

export default function StockInListPage() {
  const navigate = useNavigate()
  const [editingStockIn, setEditingStockIn] = useState<StockIn | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [materials, setMaterials] = useState<Material[]>([])
  const [loadingMaterials, setLoadingMaterials] = useState(false)
  const [editFormData, setEditFormData] = useState({
    nomor_invoice: '',
    material_id: '',
    quantity: '',
    tanggal_masuk: '',
  })
  const [editSuratJalanFiles, setEditSuratJalanFiles] = useState<File[]>([])
  const [editMaterialDatangFiles, setEditMaterialDatangFiles] = useState<File[]>([])
  const [editLoading, setEditLoading] = useState(false)
  
  const {
    data,
    loading,
    page,
    totalPages,
    searchTerm,
    startDate,
    endDate,
    setPage,
    setSearchTerm,
    onDateChange,
  } = useInventoryList<StockIn>({
    fetchFunction: async (params) => {
      return await inventoryService.getStockIns(
        params.page,
        params.limit || 10,
        params.search,
        params.startDate,
        params.endDate
      )
    },
    extractItems,
    defaultLimit: 10,
    enableAutoRefresh: true,
    autoRefreshInterval: 600000, // 10 menit
    errorMessage: 'Gagal memuat daftar barang masuk',
  })

  const handleEdit = async (stockIn: StockIn) => {
    try {
      setLoadingMaterials(true)
      // Load materials
      const materialsResponse = await inventoryService.getMaterials(1, 1000)
      const materialsItems = Array.isArray(materialsResponse?.data)
        ? materialsResponse.data
        : Array.isArray(materialsResponse)
          ? materialsResponse
          : (materialsResponse?.data?.items || materialsResponse?.data || materialsResponse?.items || [])
      setMaterials(materialsItems as Material[])
      
      // Set form data
      setEditFormData({
        nomor_invoice: stockIn.nomor_invoice,
        material_id: stockIn.material_id.toString(),
        quantity: stockIn.quantity.toString(),
        tanggal_masuk: stockIn.tanggal_masuk.split('T')[0],
      })
      setEditingStockIn(stockIn)
      setIsEditModalOpen(true)
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Gagal memuat data untuk edit',
      })
    } finally {
      setLoadingMaterials(false)
    }
  }

  const handleUpdateStockIn = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!editingStockIn) return

    // Validasi
    if (!editFormData.nomor_invoice || !editFormData.material_id || !editFormData.quantity || !editFormData.tanggal_masuk) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Semua field wajib diisi',
      })
      return
    }

    const quantity = parseFloat(editFormData.quantity)
    if (isNaN(quantity) || quantity <= 0) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Quantity harus lebih dari 0',
      })
      return
    }

    try {
      setEditLoading(true)
      await inventoryService.updateStockIn(
        editingStockIn.id,
        {
          nomor_invoice: editFormData.nomor_invoice,
          material_id: parseInt(editFormData.material_id),
          quantity: quantity,
          tanggal_masuk: editFormData.tanggal_masuk,
        },
        [], // evidence files - tidak digunakan untuk update
        editSuratJalanFiles,
        editMaterialDatangFiles
      )

      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Barang masuk berhasil diupdate',
        timer: 2000,
      })

      // Refresh list
      window.location.reload()
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || error.message || 'Gagal mengupdate barang masuk',
      })
    } finally {
      setEditLoading(false)
    }
  }

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false)
    setEditingStockIn(null)
    setEditFormData({
      nomor_invoice: '',
      material_id: '',
      quantity: '',
      tanggal_masuk: '',
    })
    setEditSuratJalanFiles([])
    setEditMaterialDatangFiles([])
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Daftar Barang Masuk</h1>
        <button
          type="button"
          onClick={() => navigate('/inventory/stock-in')}
          className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          Tambah Barang Masuk
        </button>
      </div>

      {/* Filter Section */}
      <div className="space-y-4 mb-6">
        {/* Search */}
        <div className="bg-white rounded-lg shadow p-4">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Cari nomor invoice, kode atau nama barang..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Date Range Filter */}
        <DateRangeFilter startDate={startDate} endDate={endDate} onDateChange={onDateChange} />
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tanggal</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No. Invoice</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kode</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nama Barang</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Satuan</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Evidence</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(!loading && data.length === 0) && (
                <tr>
                  <td className="px-4 py-4 text-center text-gray-500" colSpan={8}>Belum ada data</td>
                </tr>
              )}
              {data.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{new Date(row.tanggal_masuk).toLocaleDateString()}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.nomor_invoice}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.material?.kode_barang ?? '-'}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.material?.nama_barang ?? '-'}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-right">{formatDecimal(row.quantity)}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.material?.satuan ?? '-'}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                    {renderEvidenceCell(row.evidence_paths, row.surat_jalan_paths, row.material_datang_paths)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-center">
                    <button
                      type="button"
                      onClick={() => handleEdit(row)}
                      className="px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-xs"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex items-center justify-between mt-4">
        <button
          type="button"
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Sebelumnya
        </button>
        <span className="text-sm text-gray-600">
          Halaman {page} / {totalPages}
        </span>
        <button
          type="button"
          onClick={() => setPage(page + 1)}
          disabled={page >= totalPages}
          className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Berikutnya
        </button>
      </div>

      {/* Edit Modal */}
      {isEditModalOpen && editingStockIn && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Edit Barang Masuk</h2>
                <button
                  type="button"
                  onClick={handleCloseEditModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handleUpdateStockIn} className="space-y-4">
                {/* Nomor Invoice */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nomor Invoice / DO <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={editFormData.nomor_invoice}
                    onChange={(e) => setEditFormData({ ...editFormData, nomor_invoice: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Masukkan nomor invoice dari gudang pusat"
                    required
                  />
                </div>

                {/* Material */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Material <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={editFormData.material_id}
                    onChange={(e) => setEditFormData({ ...editFormData, material_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                    disabled={loadingMaterials}
                  >
                    <option value="">Pilih Material</option>
                    {materials.map((material) => (
                      <option key={material.id} value={material.id.toString()}>
                        {material.kode_barang} - {material.nama_barang}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Quantity */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={editFormData.quantity}
                    onChange={(e) => setEditFormData({ ...editFormData, quantity: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Quantity"
                    required
                  />
                </div>

                {/* Tanggal Masuk */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tanggal Masuk <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={editFormData.tanggal_masuk}
                    onChange={(e) => setEditFormData({ ...editFormData, tanggal_masuk: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                {/* Upload Surat Jalan dan Material Datang */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <EvidenceUpload
                    files={editSuratJalanFiles}
                    onChange={setEditSuratJalanFiles}
                    maxFiles={5}
                    maxSize={5}
                    label="Upload Surat Jalan (Maksimal 5 file, 5MB per file)"
                    inputId="edit-surat-jalan-upload"
                  />

                  <EvidenceUpload
                    files={editMaterialDatangFiles}
                    onChange={setEditMaterialDatangFiles}
                    maxFiles={5}
                    maxSize={5}
                    label="Upload Material Datang (Maksimal 5 file, 5MB per file)"
                    inputId="edit-material-datang-upload"
                  />
                </div>

                {/* Actions */}
                <div className="flex justify-end space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseEditModal}
                    className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Batal
                  </button>
                  <button
                    type="submit"
                    disabled={editLoading}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {editLoading ? 'Menyimpan...' : 'Simpan'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function renderEvidenceCell(
  evidencePaths?: string,
  suratJalanPaths?: string,
  materialDatangPaths?: string
) {
  // Gabungkan semua evidence paths
  const allEvidenceUrls: Array<{ url: string; type: string }> = []
  
  // Parse dan tambahkan evidence umum
  const evidenceUrls = parseEvidence(evidencePaths)
  evidenceUrls.forEach(url => {
    allEvidenceUrls.push({ url, type: 'Evidence' })
  })
  
  // Parse dan tambahkan surat jalan
  const suratJalanUrls = parseEvidence(suratJalanPaths)
  suratJalanUrls.forEach(url => {
    allEvidenceUrls.push({ url, type: 'Surat Jalan' })
  })
  
  // Parse dan tambahkan material datang
  const materialDatangUrls = parseEvidence(materialDatangPaths)
  materialDatangUrls.forEach(url => {
    allEvidenceUrls.push({ url, type: 'Material Datang' })
  })

  if (allEvidenceUrls.length === 0) {
    return <span className="text-gray-400">-</span>
  }

  const showEvidence = (url: string, type: string) => {
    const isImage = url.match(/\.(jpg|jpeg|png|gif|webp)$/i)
    const isPdf = url.match(/\.pdf$/i)
    
    if (isImage) {
      Swal.fire({
        title: type,
        html: `<img src="${url}" style="max-width:100%; border-radius:8px" />`,
        showConfirmButton: false,
        showCloseButton: true,
        width: 800,
      })
    } else if (isPdf) {
      Swal.fire({
        title: type,
        html: `<iframe src="${url}" style="width:100%; height:600px; border:none; border-radius:8px"></iframe>`,
        showConfirmButton: false,
        showCloseButton: true,
        width: 900,
      })
    } else {
      window.open(url, '_blank')
    }
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {allEvidenceUrls.slice(0, 3).map((item, idx) => (
        <button
          key={idx}
          type="button"
          onClick={() => showEvidence(item.url, item.type)}
          className="h-10 w-10 rounded overflow-hidden focus:outline-none focus:ring-2 focus:ring-sky-500 relative group"
          title={`${item.type} ${idx + 1}`}
        >
          {item.url.match(/\.pdf$/i) ? (
            <div className="h-full w-full bg-red-100 flex items-center justify-center">
              <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
          ) : (
            <img src={item.url} alt={`${item.type} ${idx + 1}`} className="h-full w-full object-cover" />
          )}
          <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white text-xs px-1 py-0.5 opacity-0 group-hover:opacity-100 transition-opacity truncate">
            {item.type}
          </div>
        </button>
      ))}
      {allEvidenceUrls.length > 3 && (
        <span className="px-2 py-1 text-xs bg-sky-100 text-sky-700 rounded" title={`Total ${allEvidenceUrls.length} file evidence`}>
          +{allEvidenceUrls.length - 3}
        </span>
      )}
    </div>
  )
}

function parseEvidence(value?: string): string[] {
  if (!value) return []
  let arr: string[] = []
  try {
    const parsed = JSON.parse(value)
    if (Array.isArray(parsed)) {
      arr = parsed.filter(Boolean)
    }
  } catch (_) {
    arr = value.split(',').map((v) => v.trim()).filter(Boolean)
  }
  // Bentuk URL absolut jika perlu
  const base = API_BASE_URL || ''
  const join = (a: string, b: string) => {
    if (!a) return b
    if (!b) return a
    const hasSlash = a.endsWith('/') || b.startsWith('/')
    return hasSlash ? `${a}${b}` : `${a}/${b}`
  }
  return arr.map((p) => (p.startsWith('http') ? p : join(base, p.startsWith('/') ? p.slice(1) : p)))
}


