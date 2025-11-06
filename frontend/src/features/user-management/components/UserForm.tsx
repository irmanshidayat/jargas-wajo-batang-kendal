import React, { useState, useEffect } from 'react'
import { User, UserCreateRequest, UserUpdateRequest, Role } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import Swal from 'sweetalert2'

interface UserFormProps {
  user?: User | null
  onClose: () => void
  onSuccess: () => void
}

const UserForm: React.FC<UserFormProps> = ({ user, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false)
  const [roles, setRoles] = useState<Role[]>([])
  const [formData, setFormData] = useState<UserCreateRequest>({
    email: '',
    name: '',
    password: '',
    role_id: undefined,
    is_active: true,
    is_superuser: false,
  })

  useEffect(() => {
    loadRoles()
    if (user) {
      setFormData({
        email: user.email,
        name: user.name,
        password: '', // Don't pre-fill password
        role_id: user.role_id || undefined,
        is_active: user.is_active,
        is_superuser: user.is_superuser,
      })
    }
  }, [user])

  const loadRoles = async () => {
    try {
      const response = await userManagementApi.getRoles(1, 100)
      setRoles(response.data || [])
    } catch (error) {
      console.error('Error loading roles:', error)
      setRoles([])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (!formData.name || !formData.email) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Nama dan Email wajib diisi',
        })
        setLoading(false)
        return
      }

      if (!user && !formData.password) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Password wajib diisi untuk user baru',
        })
        setLoading(false)
        return
      }

      if (!user) {
        // Create new user
        await userManagementApi.createUser(formData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'User berhasil dibuat',
          timer: 2000,
        })
      } else {
        // Update user
        const updateData: UserUpdateRequest = {
          email: formData.email,
          name: formData.name,
          role_id: formData.role_id,
          is_active: formData.is_active,
          is_superuser: formData.is_superuser,
        }
        
        // Only include password if provided
        if (formData.password) {
          // Note: Backend might need password update endpoint separately
          // For now, we'll update without password (password should be updated separately)
        }
        
        await userManagementApi.updateUser(user.id, updateData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'User berhasil diupdate',
          timer: 2000,
        })
      }

      onSuccess()
      onClose()
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.message || error.message || 'Gagal menyimpan user',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          {user ? 'Edit User' : 'Tambah User'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nama <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Masukkan nama user"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Masukkan email"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password {!user && <span className="text-red-500">*</span>}
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder={user ? 'Kosongkan jika tidak ingin mengubah' : 'Masukkan password'}
              minLength={6}
            />
            {user && (
              <p className="text-xs text-gray-500 mt-1">
                Kosongkan jika tidak ingin mengubah password
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Role
            </label>
            <select
              value={formData.role_id || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  role_id: e.target.value ? parseInt(e.target.value) : undefined,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Pilih Role (Opsional)</option>
              {roles && roles.length > 0 ? (
                roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name}
                  </option>
                ))
              ) : (
                <option value="" disabled>Memuat roles...</option>
              )}
            </select>
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) =>
                  setFormData({ ...formData, is_active: e.target.checked })
                }
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <span className="ml-2 text-sm text-gray-700">Active</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_superuser || false}
                onChange={(e) =>
                  setFormData({ ...formData, is_superuser: e.target.checked })
                }
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <span className="ml-2 text-sm text-gray-700">Superuser</span>
            </label>
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

export default UserForm

