import { useEffect, useState } from 'react'
import { inventoryService, Return } from '../services/inventoryService'
import { extractItems } from '@/utils/api'
import Swal from 'sweetalert2'
import { useNavigate } from 'react-router-dom'
import { getTodayDate, formatDecimal } from '../../../utils/helpers'
import DateRangeFilter from '@/components/common/DateRangeFilter'

export default function ReturnsListPage() {
  const navigate = useNavigate()
  const [items, setItems] = useState<Return[]>([])
  const [loading, setLoading] = useState(false)
  const [page] = useState(1)
  const [limit] = useState(100)
  const [searchTerm, setSearchTerm] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const loadReturns = async () => {
    try {
      setLoading(true)
      void Swal.fire({
        title: 'Memuat...',
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => Swal.showLoading(),
      })
      const res = await inventoryService.getReturns({
        page,
        limit,
        search: searchTerm || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      })
      console.log('Returns API response:', res)
      console.log('Response structure:', {
        hasSuccess: !!res?.success,
        hasData: !!res?.data,
        dataIsArray: Array.isArray(res?.data),
        dataLength: Array.isArray(res?.data) ? res.data.length : 'not array',
        hasMeta: !!res?.meta
      })
      
      // Handle different response structures
      let extracted: Return[] = []
      
      // Structure 1: { success, message, data: [...], meta: {...} } - Standard paginated response
      if (res?.success && res?.data && Array.isArray(res.data)) {
        extracted = res.data as Return[]
        console.log('Using Structure 1 (success + data array)')
      }
      // Structure 2: { data: [...], meta: {...} } - Without success flag
      else if (res?.data && Array.isArray(res.data)) {
        extracted = res.data as Return[]
        console.log('Using Structure 2 (data array without success)')
      }
      // Structure 3: { data: { items: [...] } } - Nested items
      else if (res?.data?.items && Array.isArray(res.data.items)) {
        extracted = res.data.items as Return[]
        console.log('Using Structure 3 (data.items array)')
      }
      // Structure 4: Try extractItems helper
      else {
        extracted = extractItems<Return>(res) || []
        console.log('Using Structure 4 (extractItems helper)')
      }
      
      console.log('Extracted items:', extracted)
      console.log('Items count:', extracted.length)
      
      if (extracted.length > 0) {
        console.log('First item sample:', extracted[0])
      }
      
      if (extracted.length === 0 && res) {
        console.warn('No items extracted but response exists:', JSON.stringify(res, null, 2))
        console.warn('Response data type:', typeof res.data)
        console.warn('Response data value:', res.data)
      }
      
      setItems(extracted)
      Swal.close()
    } catch (e: any) {
      Swal.close()
      console.error('Error loading returns:', e)
      Swal.fire({ 
        icon: 'error', 
        title: 'Error', 
        text: e?.response?.data?.detail || e?.message || 'Gagal memuat data retur' 
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      loadReturns()
    }, 500)

    return () => clearTimeout(debounceTimer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, startDate, endDate])

  const handleRelease = async (ret: Return) => {
    if (ret.is_released === 1) {
      Swal.fire({ icon: 'info', title: 'Info', text: 'Return sudah dikeluarkan kembali' })
      return
    }

    const { value: tanggal } = await Swal.fire<{ tanggal: string }>({
      title: 'Tanggal Keluar',
      html: `<input id="tgl" type="date" class="swal2-input" value="${getTodayDate()}" />`,
      focusConfirm: false,
      preConfirm: () => {
        const el = document.getElementById('tgl') as HTMLInputElement
        return { tanggal: el?.value }
      },
      confirmButtonText: 'Keluarkan',
      showCancelButton: true,
    })

    if (!tanggal || !tanggal.tanggal) return

    try {
      Swal.showLoading()
      await inventoryService.releaseReturn(ret.id, tanggal.tanggal, [])
      await Swal.fire({ icon: 'success', title: 'Berhasil', text: 'Return berhasil dikeluarkan kembali' })
      loadReturns()
    } catch (e: any) {
      Swal.fire({ icon: 'error', title: 'Error', text: e.response?.data?.detail || 'Gagal mengeluarkan kembali' })
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Daftar Retur</h1>
        <button
          onClick={() => navigate('/inventory/returns/create')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Tambah Retur
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
            placeholder="Cari kode/nama barang atau nama mandor..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Date Range Filter */}
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onDateChange={(start, end) => {
            setStartDate(start)
            setEndDate(end)
          }}
        />
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="overflow-x-auto w-full">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Material</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Mandor</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Qty</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Kondisi Baik</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Kondisi Reject</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Tanggal</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">No Barang Keluar</th>
                <th className="px-4 py-3 whitespace-nowrap" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {loading ? (
                <tr>
                  <td className="px-4 py-6 text-center text-gray-500" colSpan={10}>Memuat data...</td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-center text-gray-500" colSpan={10}>
                    <div className="flex flex-col items-center justify-center py-4">
                      <p className="text-gray-500 mb-2">Belum ada data retur barang</p>
                      <button
                        onClick={() => navigate('/inventory/returns/create')}
                        className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Tambah Retur Baru
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                items.map((ret) => (
                  <tr key={ret.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{ret.id}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {ret.material?.nama_barang || `Material ID: ${ret.material_id}`}
                      {ret.material?.kode_barang && (
                        <span className="ml-1 text-xs text-gray-500">({ret.material.kode_barang})</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {ret.mandor?.nama || `Mandor ID: ${ret.mandor_id}`}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 font-medium">
                      {formatDecimal(ret.quantity_kembali)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {formatDecimal(ret.quantity_kondisi_baik)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {formatDecimal(ret.quantity_kondisi_reject)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {ret.tanggal_kembali 
                        ? new Date(ret.tanggal_kembali).toLocaleDateString('id-ID', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit'
                          })
                        : '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {ret.is_released === 1 ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Sudah dikeluarkan
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Belum dikeluarkan
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {ret.stock_out?.nomor_barang_keluar || ret.nomor_barang_keluar ? (
                        <span className="font-medium text-orange-600">{ret.stock_out?.nomor_barang_keluar || ret.nomor_barang_keluar}</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <button
                        onClick={() => handleRelease(ret)}
                        className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        disabled={ret.is_released === 1 || ret.quantity_kondisi_baik === 0}
                        title={ret.is_released === 1 ? 'Return sudah dikeluarkan' : (ret.quantity_kondisi_baik === 0 ? 'Qty kondisi baik 0' : 'Keluarkan kembali ke stock out')}
                      >
                        {ret.is_released === 1 ? 'Sudah Dikeluarkan' : 'Keluarkan Kembali'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}


