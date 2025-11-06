import { useNavigate } from 'react-router-dom'
import { inventoryService, SuratPermintaan } from '../services/inventoryService'
import { extractItems } from '@/utils/api'
import Swal from 'sweetalert2'
import DateRangeFilter from '@/components/common/DateRangeFilter'
import { useInventoryList } from '../hooks/useInventoryList'
import {
  generateSuratPermintaanPDF,
  printSuratPermintaanPDF,
  type SuratPermintaanData
} from '@/utils/pdfGenerator'

export default function SuratPermintaanListPage() {
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
  } = useInventoryList<SuratPermintaan>({
    fetchFunction: async (params) => {
      return await inventoryService.getSuratPermintaans(
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
    errorMessage: 'Gagal memuat daftar surat permintaan',
  })

  const handleExportPDF = async (suratPermintaan: SuratPermintaan) => {
    try {
      const pdfData: SuratPermintaanData = {
        tanggal: suratPermintaan.tanggal,
        items: suratPermintaan.items.map((item, index) => ({
          no: index + 1,
          kodeBarang: item.kode_barang || '',
          namaBarang: item.nama_barang,
          qty: typeof item.qty === 'number' ? item.qty : parseFloat(item.qty.toString()),
          sat: item.satuan,
          sumberBarang: item.sumber_barang || {
            proyek: false,
            proyekValue: '',
            stok: false,
            stokValue: ''
          },
          peruntukan: item.peruntukan || {
            proyek: false,
            proyekValue: '',
            produksi: false,
            produksiValue: '',
            kantor: false,
            lainLain: false
          }
        })),
        signatures: suratPermintaan.signatures || {
          pemohon: '',
          menyetujui: '',
          yangMenyerahkan: '',
          mengetahuiSPV: '',
          mengetahuiAdminGudang: ''
        }
      }

      await generateSuratPermintaanPDF(pdfData)
      
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

  const handlePrintPDF = async (suratPermintaan: SuratPermintaan) => {
    try {
      const pdfData: SuratPermintaanData = {
        tanggal: suratPermintaan.tanggal,
        items: suratPermintaan.items.map((item, index) => ({
          no: index + 1,
          kodeBarang: item.kode_barang || '',
          namaBarang: item.nama_barang,
          qty: typeof item.qty === 'number' ? item.qty : parseFloat(item.qty.toString()),
          sat: item.satuan,
          sumberBarang: item.sumber_barang || {
            proyek: false,
            proyekValue: '',
            stok: false,
            stokValue: ''
          },
          peruntukan: item.peruntukan || {
            proyek: false,
            proyekValue: '',
            produksi: false,
            produksiValue: '',
            kantor: false,
            lainLain: false
          }
        })),
        signatures: suratPermintaan.signatures || {
          pemohon: '',
          menyetujui: '',
          yangMenyerahkan: '',
          mengetahuiSPV: '',
          mengetahuiAdminGudang: ''
        }
      }

      await printSuratPermintaanPDF(pdfData)
    } catch (error: any) {
      await Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error.message || 'Gagal print PDF'
      })
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4 sm:mb-0">Daftar Surat Permintaan</h1>
        <button
          type="button"
          onClick={() => navigate('/inventory/surat-permintaan')}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors w-full sm:w-auto"
        >
          Buat Surat Permintaan
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
            placeholder="Cari nomor surat atau tanggal..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
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
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nomor Surat</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tanggal</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Jumlah Item</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created By</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading && (
                <tr>
                  <td className="px-4 py-4 text-center text-gray-500" colSpan={6}>
                    Memuat data...
                  </td>
                </tr>
              )}
              {!loading && data.length === 0 && (
                <tr>
                  <td className="px-4 py-4 text-center text-gray-500" colSpan={6}>
                    Belum ada data surat permintaan
                  </td>
                </tr>
              )}
              {!loading && data.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-indigo-600">
                    {row.nomor_surat}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                    {new Date(row.tanggal).toLocaleDateString('id-ID')}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                    {row.project?.name || '-'}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-center">
                    {row.items?.length || 0}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                    {row.creator?.name || '-'}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-center">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleExportPDF(row)}
                        className="px-3 py-1.5 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-xs"
                        title="Export PDF"
                      >
                        Export
                      </button>
                      <button
                        type="button"
                        onClick={() => handlePrintPDF(row)}
                        className="px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-xs"
                        title="Print PDF"
                      >
                        Print
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {totalPages > 1 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-4 px-4 py-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>Menampilkan halaman</span>
            <span className="font-semibold text-gray-900">{page}</span>
            <span>dari</span>
            <span className="font-semibold text-gray-900">{totalPages}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1 || loading}
              className="px-4 py-2 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Sebelumnya
            </button>
            <button
              type="button"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages || loading}
              className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Berikutnya
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

