import { useEffect, useState, useMemo, useRef } from 'react'
import useDebounce from '@/hooks/useDebounce'
import { inventoryService, StockBalance, Discrepancy, Notification } from '../services/inventoryService'
import Swal from 'sweetalert2'
import ExportExcelButton from '../components/ExportExcelButton'
import DateRangeFilter from '@/components/common/DateRangeFilter'
import { formatDecimal } from '@/utils/helpers'

export default function InventoryDashboardPage() {
  const [stockBalance, setStockBalance] = useState<StockBalance[]>([])
  const [discrepancies, setDiscrepancies] = useState<Discrepancy[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const debouncedSearch = useDebounce(searchTerm, 400)
  const hasShownAlertRef = useRef(false)

  // Unified data loading function
  const loadDashboardData = async (searchOnly = false) => {
    try {
      if (!searchOnly) {
        setLoading(true)
      } else {
        setIsSearching(true)
      }
      
      const searchParam = searchOnly ? debouncedSearch.trim() || undefined : undefined
      
      if (searchOnly) {
        // Hanya load stock balance saat search (untuk performa)
        const balanceRes = await inventoryService.getStockBalance(
          undefined,
          searchParam,
          startDate || undefined,
          endDate || undefined
        )
        // extractData sudah mengembalikan data langsung (array StockBalance[])
        setStockBalance(Array.isArray(balanceRes) ? balanceRes : [])
      } else {
        // Load all data in parallel saat initial load atau filter tanggal berubah
        const [balanceRes, discrepancyRes, notificationRes] = await Promise.all([
          inventoryService.getStockBalance(
            undefined, 
            searchParam,
            startDate || undefined,
            endDate || undefined
          ),
          inventoryService.checkDiscrepancy(),
          inventoryService.getNotifications(1, 10, false),
        ])

        // extractData sudah mengembalikan data langsung
        const newBalance: StockBalance[] = Array.isArray(balanceRes) ? balanceRes : []
        const newDiscrepancies: Discrepancy[] = Array.isArray(discrepancyRes) ? discrepancyRes : []
        
        // Notifications: extractData mengembalikan response yang bisa berupa paginated atau array
        // Cek struktur untuk mendapatkan array notifications
        let notificationsData: Notification[] = []
        if (Array.isArray(notificationRes)) {
          notificationsData = notificationRes
        } else if (notificationRes?.data && Array.isArray(notificationRes.data)) {
          notificationsData = notificationRes.data
        } else if (notificationRes?.items && Array.isArray(notificationRes.items)) {
          notificationsData = notificationRes.items
        }
        
        setStockBalance(newBalance)
        setDiscrepancies(newDiscrepancies)
        setNotifications(notificationsData)

        // Show alert jika ada selisih (hanya sekali)
        const hasDiscrepancy = newDiscrepancies.some((d) => d.selisih_aktual > 0)
        if (hasDiscrepancy && newDiscrepancies.length > 0 && !hasShownAlertRef.current) {
          showDiscrepancyAlert(newDiscrepancies)
          hasShownAlertRef.current = true
        }
      }
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || (searchOnly ? 'Gagal memuat data barang' : 'Gagal memuat data dashboard'),
      })
    } finally {
      if (!searchOnly) {
        setLoading(false)
      } else {
        setIsSearching(false)
      }
    }
  }

  // Initial load dan saat filter tanggal berubah - load semua data
  useEffect(() => {
    hasShownAlertRef.current = false
    loadDashboardData(false)
    
    // Set interval untuk auto-refresh setiap 10 menit
    const interval = setInterval(() => {
      loadDashboardData(false)
    }, 600000) // 10 menit

    return () => {
      clearInterval(interval)
    }
  }, [startDate, endDate])

  // Search only - hanya load stock balance untuk performa
  useEffect(() => {
    // Skip jika ini initial render atau search kosong (akan dihandle oleh useEffect utama)
    if (debouncedSearch === '' && searchTerm === '') {
      return
    }

    const debounceTimer = setTimeout(() => {
      if (debouncedSearch.trim() === '') {
        // Jika search dikosongkan, reload semua data
        hasShownAlertRef.current = false
        loadDashboardData(false)
      } else {
        // Jika ada search, hanya load stock balance
        loadDashboardData(true)
      }
    }, 500)

    return () => clearTimeout(debounceTimer)
  }, [debouncedSearch])


  // Memoized calculations untuk optimasi
  const activeDiscrepancies = useMemo(() => {
    return discrepancies.filter((d) => d.selisih_aktual > 0)
  }, [discrepancies])

  const summaryTotals = useMemo(() => {
    return {
      totalMasuk: stockBalance.reduce((sum, item) => sum + item.total_masuk, 0),
      // Backend sudah exclude retur keluar dari total_keluar, jadi tidak perlu adjustment lagi
      totalKeluar: stockBalance.reduce((sum, item) => sum + (item.total_keluar || 0), 0),
      totalTerpasang: stockBalance.reduce((sum, item) => sum + (item.total_terpasang || 0), 0),
      // Backend sudah menghitung stock_saat_ini dengan benar (exclude retur keluar)
      // Gunakan stock_saat_ini langsung dari backend untuk konsistensi
      totalStockSaatIni: stockBalance.reduce((sum, item) => sum + (item.stock_saat_ini || 0), 0),
    }
  }, [stockBalance])

  const showDiscrepancyAlert = (discrepanciesData: Discrepancy[]) => {
    const unreadCount = discrepanciesData.filter((d) => d.selisih_aktual > 0).length
    if (unreadCount > 0) {
      Swal.fire({
        icon: 'warning',
        title: 'Peringatan Selisih Barang',
        html: `Ada <strong>${unreadCount}</strong> mandor dengan selisih barang pengembalian yang belum dicatat.<br/>Silakan cek detail di bawah.`,
        confirmButtonText: 'OK',
        confirmButtonColor: '#3b82f6',
      })
    }
  }

  // Export dipindah ke komponen terpisah agar modular dan reusable

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Memuat data...</div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-full overflow-x-hidden px-2 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6">
      <div className="w-full max-w-full overflow-x-hidden space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Dashboard Inventory</h1>
          <ExportExcelButton 
            currentSearch={searchTerm} 
            startDate={startDate || undefined}
            endDate={endDate || undefined}
          />
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-blue-50 p-4 sm:p-6 rounded-lg">
          <div className="text-xs sm:text-sm text-blue-600 font-medium">Total Barang Masuk</div>
          <div className="text-xl sm:text-2xl font-bold text-blue-900 mt-2">
            {formatDecimal(summaryTotals.totalMasuk)}
          </div>
        </div>
        <div className="bg-red-50 p-4 sm:p-6 rounded-lg">
          <div className="text-xs sm:text-sm text-red-600 font-medium">Total Barang Keluar</div>
          <div className="text-xl sm:text-2xl font-bold text-red-900 mt-2">
            {formatDecimal(summaryTotals.totalKeluar)}
          </div>
        </div>
        <div className="bg-yellow-50 p-4 sm:p-6 rounded-lg">
          <div className="text-xs sm:text-sm text-yellow-600 font-medium">Barang Terpasang</div>
          <div className="text-xl sm:text-2xl font-bold text-yellow-900 mt-2">
            {formatDecimal(summaryTotals.totalTerpasang)}
          </div>
        </div>
        <div className="bg-green-50 p-4 sm:p-6 rounded-lg">
          <div className="text-xs sm:text-sm text-green-600 font-medium">Stock Saat Ini</div>
          <div className="text-xl sm:text-2xl font-bold text-green-900 mt-2">
            {formatDecimal(summaryTotals.totalStockSaatIni)}
          </div>
        </div>
      </div>

        {/* Notifications */}
        {notifications.length > 0 && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 sm:p-4 rounded w-full">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <h3 className="text-xs sm:text-sm font-medium text-yellow-800">
                  Ada {notifications.length} Notifikasi
                </h3>
                <div className="mt-2 text-xs sm:text-sm text-yellow-700">
                  {notifications.slice(0, 3).map((notif) => (
                    <p key={notif.id} className="break-words">{notif.message}</p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Discrepancy Table */}
        {activeDiscrepancies.length > 0 && (
          <div className="bg-white rounded-lg shadow p-3 sm:p-4 md:p-6 w-full max-w-full overflow-x-hidden">
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">
              Peringatan Selisih Barang Pengembalian
            </h2>
            <div className="w-full overflow-x-hidden">
              <table className="w-full table-auto divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Mandor
                    </th>
                    <th className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Material
                    </th>
                    <th className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Keluar
                    </th>
                    <th className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Terpasang
                    </th>
                    <th className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Kembali Dicatat
                    </th>
                    <th className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Selisih
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {activeDiscrepancies.map((disc, idx) => (
                      <tr key={idx} className={disc.status === 'warning' ? 'bg-yellow-50' : ''}>
                        <td className="px-2 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-gray-900">
                          {disc.mandor_nama}
                        </td>
                        <td className="px-2 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                          {disc.material_nama}
                        </td>
                        <td className="px-2 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                          {disc.barang_keluar}
                        </td>
                        <td className="px-2 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                          {disc.barang_terpasang}
                        </td>
                        <td className="px-2 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                          {disc.barang_kembali_dicatat}
                        </td>
                        <td className="px-2 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-bold text-red-600">
                          {disc.selisih_aktual}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Stock Balance Table */}
        <div className="bg-white rounded-lg shadow p-3 sm:p-4 md:p-6 w-full max-w-full overflow-x-hidden">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-3 sm:mb-4">
            <h2 className="text-base sm:text-lg font-semibold text-gray-900">Stock Balance</h2>
          </div>

          {/* Filter Section */}
          <div className="space-y-3 sm:space-y-4 mb-4 sm:mb-6">
            {/* Search */}
            <div className="bg-gray-50 rounded-lg p-3 sm:p-4 w-full">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Cari barang (nama atau kode)..."
                className="w-full max-w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Date Range Filter */}
            <div className="w-full max-w-full">
              <DateRangeFilter
                startDate={startDate}
                endDate={endDate}
                onDateChange={(start, end) => {
                  setStartDate(start)
                  setEndDate(end)
                }}
                label="Filter Tanggal"
              />
            </div>
          </div>
          <div className="w-full overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Kode
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Nama Barang
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Masuk
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Keluar
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Terpasang
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Kembali
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Kondisi Baik
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Kondisi Reject
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Stok Ready
                  </th>
                  <th className="px-2 sm:px-3 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Stock Saat Ini
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stockBalance.map((item) => (
                  <tr key={item.material_id}>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-gray-900">
                      {item.kode_barang}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                      {item.nama_barang}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                      {formatDecimal(item.total_masuk)}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                      {formatDecimal(item.total_keluar || 0)}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-yellow-600">
                      {formatDecimal(item.total_terpasang || 0)}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                      {formatDecimal(item.total_kembali)}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-green-600">
                      {formatDecimal(item.total_kondisi_baik ?? 0)}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-red-600">
                      {formatDecimal(item.total_kondisi_reject ?? 0)}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-bold text-blue-600">
                      {formatDecimal(item.stock_ready ?? 0)}
                    </td>
                    <td className="px-2 sm:px-3 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-bold text-green-600">
                      {formatDecimal(item.stock_saat_ini ?? 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

