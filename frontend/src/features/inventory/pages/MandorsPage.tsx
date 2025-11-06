import { useState, useEffect } from 'react'
import { inventoryService, Mandor, MandorCreateRequest } from '../services/inventoryService'
import Swal from 'sweetalert2'

export default function MandorsPage() {
  const [mandors, setMandors] = useState<Mandor[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingMandor, setEditingMandor] = useState<Mandor | null>(null)
  const [formData, setFormData] = useState<MandorCreateRequest>({
    nama: '',
    nomor_kontak: '',
    alamat: '',
  })

  useEffect(() => {
    loadMandors()
  }, [])

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      loadMandors(1, 100, searchTerm || undefined)
    }, 500)
    return () => clearTimeout(debounceTimer)
  }, [searchTerm])

  const loadMandors = async (page = 1, limit = 100, search?: string) => {
    try {
      setLoading(true)
      const response = await inventoryService.getMandors(page, limit, search)
      // extractPaginatedResponse mengembalikan: { data: [...], total, page, limit, message }
      setMandors(response.data || [])
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error?.response?.data?.detail || 'Gagal memuat data mandors',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (mandor?: Mandor) => {
    if (mandor) {
      setEditingMandor(mandor)
      setFormData({
        nama: mandor.nama,
        nomor_kontak: mandor.nomor_kontak || '',
        alamat: mandor.alamat || '',
      })
    } else {
      setEditingMandor(null)
      setFormData({
        nama: '',
        nomor_kontak: '',
        alamat: '',
      })
    }
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingMandor(null)
    setFormData({
      nama: '',
      nomor_kontak: '',
      alamat: '',
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.nama) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Nama Mandor wajib diisi',
      })
      return
    }

    try {
      setLoading(true)
      if (editingMandor) {
        await inventoryService.updateMandor(editingMandor.id, formData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Mandor berhasil diupdate',
          timer: 2000,
        })
      } else {
        await inventoryService.createMandor(formData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Mandor berhasil ditambahkan',
          timer: 2000,
        })
      }

      handleCloseModal()
      loadMandors(1, 100, searchTerm || undefined)
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || 'Gagal menyimpan mandor',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Master Mandor</h1>
        <button
          onClick={() => handleOpenModal()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors w-full sm:w-auto"
        >
          + Tambah Mandor
        </button>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Cari mandor (nama)..."
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
                  Nama Mandor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Nomor Kontak
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Alamat
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
              {loading && mandors.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    Memuat data...
                  </td>
                </tr>
              ) : mandors.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    Tidak ada data mandor
                  </td>
                </tr>
              ) : (
                mandors.map((mandor) => (
                  <tr key={mandor.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {mandor.nama}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {mandor.nomor_kontak || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {mandor.alamat || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          mandor.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {mandor.is_active ? 'Aktif' : 'Tidak Aktif'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleOpenModal(mandor)}
                        className="text-indigo-600 hover:text-indigo-900 mr-4"
                      >
                        Edit
                      </button>
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
              {editingMandor ? 'Edit Mandor' : 'Tambah Mandor'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nama Mandor <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.nama}
                  onChange={(e) => setFormData({ ...formData, nama: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Masukkan nama mandor"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nomor Kontak
                </label>
                <input
                  type="text"
                  value={formData.nomor_kontak}
                  onChange={(e) => setFormData({ ...formData, nomor_kontak: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Masukkan nomor kontak (opsional)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Alamat
                </label>
                <textarea
                  value={formData.alamat}
                  onChange={(e) => setFormData({ ...formData, alamat: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Masukkan alamat (opsional)"
                  rows={3}
                />
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
    </div>
  )
}

