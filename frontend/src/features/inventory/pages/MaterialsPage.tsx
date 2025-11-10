import { useState, useEffect } from 'react'
import { inventoryService, Material, MaterialCreateRequest } from '../services/inventoryService'
import Swal from 'sweetalert2'
import SelectWithSearch from '../components/SelectWithSearch'

// Helper function untuk format Rupiah
const formatRupiah = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

export default function MaterialsPage() {
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [importFile, setImportFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)
  const [editingMaterial, setEditingMaterial] = useState<Material | null>(null)
  const [formData, setFormData] = useState<MaterialCreateRequest>({
    kode_barang: '',
    nama_barang: '',
    satuan: '',
    kategori: '',
    harga: null,
  })
  const [uniqueSatuans, setUniqueSatuans] = useState<string[]>([])
  const [uniqueKategoris, setUniqueKategoris] = useState<string[]>([])

  useEffect(() => {
    loadMaterials()
  }, [])

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      loadMaterials(1, 100, searchTerm || undefined)
    }, 500)
    return () => clearTimeout(debounceTimer)
  }, [searchTerm])

  const loadMaterials = async (page = 1, limit = 100, search?: string) => {
    try {
      setLoading(true)
      const response = await inventoryService.getMaterials(page, limit, search)
      const items = Array.isArray(response?.data)
        ? response.data
        : Array.isArray(response)
          ? response
          : (response?.data?.items || response?.data || response?.items || [])
      setMaterials(items as Material[])
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Gagal memuat data materials',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = async (material?: Material) => {
    if (material) {
      setEditingMaterial(material)
      setFormData({
        kode_barang: material.kode_barang,
        nama_barang: material.nama_barang,
        satuan: material.satuan,
        kategori: material.kategori || '',
        harga: material.harga || null,
      })
    } else {
      setEditingMaterial(null)
      setFormData({
        kode_barang: '',
        nama_barang: '',
        satuan: '',
        kategori: '',
        harga: null,
      })
    }
    
    // Load unique values saat modal dibuka
    try {
      const [satuans, kategoris] = await Promise.all([
        inventoryService.getUniqueSatuans(),
        inventoryService.getUniqueKategoris(),
      ])
      setUniqueSatuans(satuans)
      setUniqueKategoris(kategoris)
    } catch (error: any) {
      console.error('Error loading unique values:', error)
    }
    
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingMaterial(null)
    setFormData({
      kode_barang: '',
      nama_barang: '',
      satuan: '',
      kategori: '',
      harga: null,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

  if (!formData.nama_barang || !formData.satuan) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Nama Barang dan Satuan wajib diisi',
      })
      return
    }

    try {
      setLoading(true)
      if (editingMaterial) {
        await inventoryService.updateMaterial(editingMaterial.id, formData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Material berhasil diupdate',
          timer: 2000,
        })
      } else {
        await inventoryService.createMaterial(formData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Material berhasil ditambahkan',
          timer: 2000,
        })
      }

      handleCloseModal()
      loadMaterials(1, 100, searchTerm || undefined)
      
      // Reload unique values setelah submit berhasil
      try {
        const [satuans, kategoris] = await Promise.all([
          inventoryService.getUniqueSatuans(),
          inventoryService.getUniqueKategoris(),
        ])
        setUniqueSatuans(satuans)
        setUniqueKategoris(kategoris)
      } catch (error: any) {
        console.error('Error reloading unique values:', error)
      }
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || 'Gagal menyimpan material',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validasi file type
    if (!file.name.endsWith('.xlsx')) {
      Swal.fire({
        icon: 'error',
        title: 'Format File Tidak Valid',
        text: 'Hanya file .xlsx yang diperbolehkan',
      })
      e.target.value = ''
      return
    }

    // Validasi file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      Swal.fire({
        icon: 'error',
        title: 'Ukuran File Terlalu Besar',
        text: 'Ukuran file maksimal 10MB',
      })
      e.target.value = ''
      return
    }

    setImportFile(file)
  }

  const handleImportSubmit = async () => {
    if (!importFile) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Silakan pilih file Excel terlebih dahulu',
      })
      return
    }

    try {
      setImporting(true)
      const response = await inventoryService.bulkImportMaterials(importFile)

      // extractData sudah mengembalikan data langsung dari backend response
      // Backend response: { success, message, data: { success_count, ... } }
      // extractData mengembalikan: { success_count, ... }
      const result = response || {}
      const successCount = result.success_count || 0
      const validationFailedCount = result.validation_failed_count || 0
      const processingFailedCount = result.processing_failed_count || 0
      const validationErrors = result.validation_errors || []
      const processingErrors = result.processing_errors || []
      const allErrors = result.errors || [] // Backward compatibility

      let htmlMessage = `<div style="text-align: left;">`
      htmlMessage += `<p><strong>Hasil Import:</strong></p>`
      htmlMessage += `<ul>`
      htmlMessage += `<li>Sukses: <strong>${successCount}</strong> material</li>`
      
      if (validationFailedCount > 0) {
        htmlMessage += `<li>Data tidak valid (tidak masuk database): <strong>${validationFailedCount}</strong> material</li>`
      }
      
      if (processingFailedCount > 0) {
        htmlMessage += `<li>Gagal saat insert: <strong>${processingFailedCount}</strong> material</li>`
      }
      
      // Backward compatibility: jika menggunakan format lama
      if (validationFailedCount === 0 && processingFailedCount === 0) {
        const oldFailedCount = result.failed_count || 0
        if (oldFailedCount > 0) {
          htmlMessage += `<li>Gagal: <strong>${oldFailedCount}</strong> material</li>`
        }
      }
      
      htmlMessage += `</ul>`

      // Tampilkan errors jika ada
      const errorsToShow = allErrors.length > 0 ? allErrors : [...validationErrors, ...processingErrors]
      
      if (errorsToShow.length > 0 && errorsToShow.length <= 10) {
        htmlMessage += `<p><strong>Detail Error:</strong></p>`
        htmlMessage += `<ul style="max-height: 200px; overflow-y: auto;">`
        errorsToShow.forEach((error: string) => {
          htmlMessage += `<li style="font-size: 12px; margin-bottom: 5px;">${error}</li>`
        })
        htmlMessage += `</ul>`
      } else if (errorsToShow.length > 10) {
        htmlMessage += `<p><strong>Detail Error (menampilkan 10 pertama dari ${errorsToShow.length}):</strong></p>`
        htmlMessage += `<ul style="max-height: 200px; overflow-y: auto;">`
        errorsToShow.slice(0, 10).forEach((error: string) => {
          htmlMessage += `<li style="font-size: 12px; margin-bottom: 5px;">${error}</li>`
        })
        htmlMessage += `</ul>`
      }

      htmlMessage += `</div>`

      // Logika notifikasi yang lebih akurat
      // Jika ada data yang berhasil masuk, tampilkan success atau warning (bukan error)
      if (successCount > 0) {
        // Ada data yang berhasil masuk
        if (validationFailedCount === 0 && processingFailedCount === 0) {
          // Semua berhasil
          await Swal.fire({
            icon: 'success',
            title: 'Import Berhasil',
            html: htmlMessage,
            confirmButtonText: 'OK',
          })
        } else {
          // Sebagian berhasil
          await Swal.fire({
            icon: 'success',
            title: 'Import Berhasil',
            html: htmlMessage,
            confirmButtonText: 'OK',
          })
        }
      } else {
        // Tidak ada yang berhasil masuk
        if (validationFailedCount > 0 || processingFailedCount > 0) {
          // Ada data yang gagal
          await Swal.fire({
            icon: 'error',
            title: 'Import Gagal',
            html: htmlMessage,
            confirmButtonText: 'OK',
          })
        } else {
          // Tidak ada data sama sekali
          await Swal.fire({
            icon: 'error',
            title: 'Import Gagal',
            html: htmlMessage,
            confirmButtonText: 'OK',
          })
        }
      }

      // Reset dan refresh
      setImportFile(null)
      setShowImportModal(false)
      const fileInput = document.getElementById('excel-file-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''

      // Refresh materials list jika ada yang sukses
      if (successCount > 0) {
        loadMaterials(1, 100, searchTerm || undefined)
      }
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.message || error.message || 'Gagal mengimpor file Excel',
      })
    } finally {
      setImporting(false)
    }
  }

  const handleCloseImportModal = () => {
    setShowImportModal(false)
    setImportFile(null)
    const fileInput = document.getElementById('excel-file-input') as HTMLInputElement
    if (fileInput) fileInput.value = ''
  }

  const handleDelete = async (material: Material) => {
    const result = await Swal.fire({
      title: 'Hapus Material?',
      html: `<p>Apakah Anda yakin ingin menghapus material:</p><p><strong>${material.nama_barang}</strong></p><p>${material.kode_barang ? `Kode: ${material.kode_barang}` : ''}</p>`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#dc2626',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Ya, Hapus',
      cancelButtonText: 'Batal',
    })

    if (result.isConfirmed) {
      try {
        setLoading(true)
        await inventoryService.deleteMaterial(material.id)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Material berhasil dihapus',
          timer: 2000,
        })
        loadMaterials(1, 100, searchTerm || undefined)
      } catch (error: any) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.message || error.message || 'Gagal menghapus material',
        })
      } finally {
        setLoading(false)
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Master Material</h1>
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <button
            onClick={() => setShowImportModal(true)}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors w-full sm:w-auto"
          >
            📥 Import Excel
          </button>
          <button
            onClick={() => handleOpenModal()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors w-full sm:w-auto"
          >
            + Tambah Material
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Cari material (kode atau nama)..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-indigo-50 to-purple-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Kode Barang
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Nama Barang
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Satuan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Kategori
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Harga
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Aksi
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading && materials.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    Memuat data...
                  </td>
                </tr>
              ) : materials.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    Tidak ada data material
                  </td>
                </tr>
              ) : (
                materials.map((material) => (
                  <tr key={material.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {material.kode_barang}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {material.nama_barang}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {material.satuan}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {material.kategori || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {formatRupiah(material.harga)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          material.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {material.is_active ? 'Aktif' : 'Tidak Aktif'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={() => handleOpenModal(material)}
                          className="p-2 text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 rounded-lg transition-colors"
                          title="Edit"
                          disabled={loading}
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(material)}
                          className="p-2 text-red-600 hover:text-red-900 hover:bg-red-50 rounded-lg transition-colors"
                          title="Hapus"
                          disabled={loading}
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {editingMaterial ? 'Edit Material' : 'Tambah Material'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kode Barang
                </label>
                <input
                  type="text"
                  value={formData.kode_barang}
                  onChange={(e) => setFormData({ ...formData, kode_barang: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Masukkan kode barang"
                />
                <p className="text-xs text-gray-500 mt-1">Opsional. Jika diisi harus unik.</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nama Barang <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.nama_barang}
                  onChange={(e) => setFormData({ ...formData, nama_barang: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Masukkan nama barang"
                  required
                />
              </div>

              <SelectWithSearch
                value={formData.satuan}
                onChange={(value) => setFormData({ ...formData, satuan: value })}
                options={uniqueSatuans}
                placeholder="Cari atau pilih satuan (contoh: kg, pcs, m)"
                label="Satuan"
                required
                disabled={loading}
                onAddNew={async (newValue) => {
                  // Nilai baru langsung digunakan, tidak perlu API call tambahan
                  // karena nilai akan disimpan saat submit form
                  setUniqueSatuans([...uniqueSatuans, newValue])
                }}
              />

              <SelectWithSearch
                value={formData.kategori || ''}
                onChange={(value) => setFormData({ ...formData, kategori: value })}
                options={uniqueKategoris}
                placeholder="Cari atau pilih kategori"
                label="Kategori"
                disabled={loading}
                onAddNew={async (newValue) => {
                  // Nilai baru langsung digunakan, tidak perlu API call tambahan
                  // karena nilai akan disimpan saat submit form
                  setUniqueKategoris([...uniqueKategoris, newValue])
                }}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Harga
                </label>
                <input
                  type="number"
                  value={formData.harga || ''}
                  onChange={(e) => {
                    const value = e.target.value === '' ? null : parseFloat(e.target.value)
                    setFormData({ ...formData, harga: value !== null && !isNaN(value) ? value : null })
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Masukkan harga (contoh: 150000)"
                  min="0"
                  step="0.01"
                />
                <p className="text-xs text-gray-500 mt-1">Opsional. Format: angka tanpa titik (contoh: 150000)</p>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  disabled={loading}
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Menyimpan...' : 'Simpan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Import Excel Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Import Material dari Excel
            </h2>

            <div className="space-y-4 mb-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800 font-semibold mb-2">
                  Format Excel yang Diperlukan:
                </p>
                <ul className="text-xs text-blue-700 space-y-1 list-disc list-inside">
                  <li>Header di row pertama: NO, NAMA BARANG, KODE BARANG, SATUAN, KATEGORI, HARGA</li>
                  <li>Data mulai dari row kedua</li>
                  <li>File format: .xlsx (Excel 2007+)</li>
                  <li>Ukuran maksimal: 10MB</li>
                </ul>
                <p className="text-sm text-blue-800 font-semibold mt-3 mb-2">
                  Kategori yang Valid:
                </p>
                <ul className="text-xs text-blue-700 space-y-1">
                  <li>• PIPA DITRIBUSI</li>
                  <li>• BUNGAN RUMAH</li>
                  <li>• BUNGAN KOMPOR</li>
                </ul>
                <div className="mt-3 pt-3 border-t border-blue-200">
                  <button
                    onClick={async () => {
                      try {
                        await inventoryService.downloadMaterialTemplate()
                        Swal.fire({
                          icon: 'success',
                          title: 'Berhasil',
                          text: 'Template Excel berhasil didownload',
                          timer: 2000,
                        })
                      } catch (error: any) {
                        Swal.fire({
                          icon: 'error',
                          title: 'Error',
                          text: error.response?.data?.message || error.message || 'Gagal mendownload template',
                        })
                      }
                    }}
                    className="w-full px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    📥 Download Template Excel
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pilih File Excel (.xlsx)
                </label>
                <input
                  id="excel-file-input"
                  type="file"
                  accept=".xlsx"
                  onChange={handleFileSelect}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  disabled={importing}
                />
                {importFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    File terpilih: <span className="font-medium">{importFile.name}</span> ({(importFile.size / 1024).toFixed(2)} KB)
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-4 pt-4">
              <button
                type="button"
                onClick={handleCloseImportModal}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                disabled={importing}
              >
                Batal
              </button>
              <button
                type="button"
                onClick={handleImportSubmit}
                disabled={importing || !importFile}
                className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {importing ? 'Mengimpor...' : 'Import'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
