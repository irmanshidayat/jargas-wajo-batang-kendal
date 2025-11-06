import { useNavigate } from 'react-router-dom'
import { inventoryService, StockOut } from '../services/inventoryService'
import { extractItems } from '@/utils/api'
import Swal from 'sweetalert2'
import DateRangeFilter from '@/components/common/DateRangeFilter'
import { useInventoryList } from '../hooks/useInventoryList'
import { API_BASE_URL } from '@/utils/constants'
import { formatDecimal } from '@/utils/helpers'

export default function StockOutListPage() {
  const navigate = useNavigate()
  
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
  } = useInventoryList<StockOut>({
    fetchFunction: async (params) => {
      return await inventoryService.getStockOuts(
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
    errorMessage: 'Gagal memuat daftar barang keluar',
  })

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Daftar Barang Keluar</h1>
        <button
          type="button"
          onClick={() => navigate('/inventory/stock-out')}
          className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          Tambah Barang Keluar
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
            placeholder="Cari nomor barang keluar, kode/nama barang, atau nama mandor..."
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
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No. Barang Keluar</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kode</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nama Barang</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Satuan</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mandor</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Evidence</th>
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
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{new Date(row.tanggal_keluar).toLocaleDateString()}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.nomor_barang_keluar}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.material?.kode_barang ?? '-'}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.material?.nama_barang ?? '-'}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-right">{formatDecimal(row.quantity)}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.material?.satuan ?? '-'}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{row.mandor?.nama ?? '-'}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                    {renderEvidenceCell(row.evidence_paths, row.surat_permohonan_paths, row.surat_serah_terima_paths)}
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
    </div>
  )
}

function renderEvidenceCell(
  evidencePaths?: string,
  suratPermohonanPaths?: string,
  suratSerahTerimaPaths?: string
) {
  // Gabungkan semua evidence paths
  const allEvidenceUrls: Array<{ url: string; type: string }> = []
  
  // Parse dan tambahkan evidence umum
  const evidenceUrls = parseEvidence(evidencePaths)
  evidenceUrls.forEach(url => {
    allEvidenceUrls.push({ url, type: 'Evidence' })
  })
  
  // Parse dan tambahkan surat permohonan
  const permohonanUrls = parseEvidence(suratPermohonanPaths)
  permohonanUrls.forEach(url => {
    allEvidenceUrls.push({ url, type: 'Surat Permohonan' })
  })
  
  // Parse dan tambahkan surat serah terima
  const serahTerimaUrls = parseEvidence(suratSerahTerimaPaths)
  serahTerimaUrls.forEach(url => {
    allEvidenceUrls.push({ url, type: 'Surat Serah Terima' })
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
  const base = API_BASE_URL || ''
  const join = (a: string, b: string) => {
    if (!a) return b
    if (!b) return a
    const hasSlash = a.endsWith('/') || b.startsWith('/')
    return hasSlash ? `${a}${b}` : `${a}/${b}`
  }
  return arr.map((p) => (p.startsWith('http') ? p : join(base, p.startsWith('/') ? p.slice(1) : p)))
}


