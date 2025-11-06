import Swal from 'sweetalert2'
import { inventoryService } from '../services/inventoryService'

interface ExportExcelButtonProps {
  currentSearch?: string
  startDate?: string
  endDate?: string
}

export default function ExportExcelButton({ currentSearch, startDate, endDate }: ExportExcelButtonProps) {
  const handleClick = async () => {
    const choice = await Swal.fire({
      title: 'Export Excel',
      text: 'Pilih sumber data',
      showDenyButton: true,
      confirmButtonText: 'Semua data',
      denyButtonText: 'Data dengan filter',
      confirmButtonColor: '#16a34a',
      denyButtonColor: '#2563eb',
    })

    const scopeAll = choice.isConfirmed
    const scopeFiltered = choice.isDenied
    if (!scopeAll && !scopeFiltered) return

    Swal.fire({
      title: 'Menyiapkan file...',
      text: 'Mohon tunggu sebentar',
      allowOutsideClick: false,
      allowEscapeKey: false,
      didOpen: () => {
        Swal.showLoading()
      },
    })

    try {
      if (scopeAll) {
        await inventoryService.exportExcel({})
      } else if (scopeFiltered) {
        await inventoryService.exportExcel({
          search: (currentSearch || '').trim() || undefined,
          start_date: startDate || undefined,
          end_date: endDate || undefined,
        })
      }
      
      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Laporan berhasil di-export ke Excel',
        timer: 2000,
        showConfirmButton: false,
      })
    } catch (error: any) {
      console.error('Export error:', error)
      await Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error?.response?.data?.detail || error?.message || 'Export Excel gagal. Silakan coba lagi.',
      })
    }
  }

  return (
    <button onClick={handleClick} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
      Export Excel
    </button>
  )
}


