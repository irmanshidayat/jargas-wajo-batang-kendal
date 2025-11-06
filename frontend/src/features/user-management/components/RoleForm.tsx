import React, { useState } from 'react'
import { Role, RoleCreateRequest, RoleUpdateRequest } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import Swal from 'sweetalert2'

interface RoleFormProps {
  role?: Role | null
  onClose: () => void
  onSuccess: () => void
}

const RoleForm: React.FC<RoleFormProps> = ({ role, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState<RoleCreateRequest>({
    name: '',
    description: '',
  })

  React.useEffect(() => {
    if (role) {
      setFormData({
        name: role.name,
        description: role.description || '',
      })
    }
  }, [role])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (!formData.name) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Nama Role wajib diisi',
        })
        setLoading(false)
        return
      }

      if (role) {
        const updateData: RoleUpdateRequest = {
          name: formData.name,
          description: formData.description,
        }
        await userManagementApi.updateRole(role.id, updateData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Role berhasil diupdate',
          timer: 2000,
        })
      } else {
        await userManagementApi.createRole(formData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Role berhasil dibuat',
          timer: 2000,
        })
      }

      onSuccess()
      onClose()
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.message || error.message || 'Gagal menyimpan role',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          {role ? 'Edit Role' : 'Tambah Role'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nama Role <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Masukkan nama role"
              required
              minLength={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Deskripsi
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Masukkan deskripsi role (opsional)"
              rows={3}
            />
          </div>

          <div className="flex justify-end space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
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
  )
}

export default RoleForm

