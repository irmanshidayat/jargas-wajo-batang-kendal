import { useNavigate } from 'react-router-dom'
import { inventoryService, SuratJalan } from '../services/inventoryService'
import { extractItems } from '@/utils/api'
import Swal from 'sweetalert2'
import DateRangeFilter from '@/components/common/DateRangeFilter'
import { useInventoryList } from '../hooks/useInventoryList'
import {
  generateSuratJalanPDF,
  printSuratJalanPDF,
  type SuratJalanData
} from '@/utils/pdfGenerator'
import { Pagination, PageHeader, SearchBox } from '@/components/common'

export default function SuratJalanListPage() {
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
  } = useInventoryList<SuratJalan>({
    fetchFunction: async (params) => {
      return await inventoryService.getSuratJalans(
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
    errorMessage: 'Gagal memuat daftar surat jalan',
  })

  const handleExportPDF = async (suratJalan: SuratJalan) => {
    try {
      const pdfData: SuratJalanData = {
        nomorForm: suratJalan.nomor_form,
        kepada: suratJalan.kepada,
        tanggalPengiriman: suratJalan.tanggal_pengiriman,
        items: suratJalan.items.map((item, index) => ({
          no: index + 1,
          namaBarang: item.nama_barang,
          qty: typeof item.qty === 'number' ? item.qty : parseFloat(item.qty.toString()),
          ket: item.keterangan || undefined
        })),
        namaPemberi: suratJalan.nama_pemberi || undefined,
        namaPenerima: suratJalan.nama_penerima || undefined,
        tanggalDiterima: suratJalan.tanggal_diterima || undefined
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

  const handlePrintPDF = async (suratJalan: SuratJalan) => {
    try {
      const pdfData: SuratJalanData = {
        nomorForm: suratJalan.nomor_form,
        kepada: suratJalan.kepada,
        tanggalPengiriman: suratJalan.tanggal_pengiriman,
        items: suratJalan.items.map((item, index) => ({
          no: index + 1,
          namaBarang: item.nama_barang,
          qty: typeof item.qty === 'number' ? item.qty : parseFloat(item.qty.toString()),
          ket: item.keterangan || undefined
        })),
        namaPemberi: suratJalan.nama_pemberi || undefined,
        namaPenerima: suratJalan.nama_penerima || undefined,
        tanggalDiterima: suratJalan.tanggal_diterima || undefined
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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <PageHeader
        title="Daftar Surat Jalan"
        description="Kelola dan lihat semua surat jalan yang telah dibuat"
        actionButton={
          <button
            type="button"
            onClick={() => navigate('/inventory/surat-jalan')}
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-lg hover:from-amber-600 hover:to-orange-700 transition-all shadow-md font-semibold w-full sm:w-auto"
          >
            Buat Surat Jalan
          </button>
        }
      />

      {/* Search and Filter */}
      <div className="mb-6 space-y-4">
        <SearchBox
          value={searchTerm}
          onChange={setSearchTerm}
          placeholder="Cari berdasarkan nomor form atau kepada..."
        />
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onDateChange={onDateChange}
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading && data.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            Memuat data...
          </div>
        ) : data.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            Tidak ada data surat jalan
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gradient-to-r from-amber-50 to-orange-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    No. Form
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Kepada
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Tanggal Pengiriman
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Jumlah Item
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Nama Pemberi
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Nama Penerima
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Aksi
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.map((suratJalan) => (
                  <tr key={suratJalan.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {suratJalan.nomor_form}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                      {suratJalan.kepada}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                      {new Date(suratJalan.tanggal_pengiriman).toLocaleDateString('id-ID')}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                      {suratJalan.items?.length || 0} item
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                      {suratJalan.nama_pemberi || '-'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                      {suratJalan.nama_penerima || '-'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleExportPDF(suratJalan)}
                          className="text-amber-600 hover:text-amber-900 font-semibold"
                          title="Export PDF"
                        >
                          Export
                        </button>
                        <span className="text-gray-300">|</span>
                        <button
                          onClick={() => handlePrintPDF(suratJalan)}
                          className="text-orange-600 hover:text-orange-900 font-semibold"
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
        )}
      </div>

      {/* Pagination */}
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
        loading={loading}
      />
    </div>
  )
}

