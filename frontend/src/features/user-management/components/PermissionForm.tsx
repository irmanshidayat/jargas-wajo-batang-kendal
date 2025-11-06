import React, { useState, useEffect, useMemo } from 'react'
import { Permission, PermissionCreateRequest, PermissionUpdateRequest, Page } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import Swal from 'sweetalert2'

interface PermissionFormProps {
  permission?: Permission | null
  pageId?: number
  onClose: () => void
  onSuccess: () => void
}

const PermissionForm: React.FC<PermissionFormProps> = ({
  permission,
  pageId,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false)
  const [loadingPages, setLoadingPages] = useState(false)
  const [pages, setPages] = useState<Page[]>([])
  const [formData, setFormData] = useState<PermissionCreateRequest>({
    page_id: pageId || 0,
    can_create: false,
    can_read: false,
    can_update: false,
    can_delete: false,
  })

  useEffect(() => {
    loadPages()
    if (permission) {
      setFormData({
        page_id: permission.page_id,
        can_create: permission.can_create,
        can_read: permission.can_read,
        can_update: permission.can_update,
        can_delete: permission.can_delete,
      })
    }
  }, [permission, pageId])

  const loadPages = async () => {
    try {
      setLoadingPages(true)
      const response = await userManagementApi.getPages(1, 100)
      setPages(Array.isArray(response.data) ? response.data : response.data || [])
    } catch (error) {
      console.error('Error loading pages:', error)
      setPages([])
    } finally {
      setLoadingPages(false)
    }
  }

  // Check apakah semua permissions checked
  const allPermissionsChecked = useMemo(() => {
    return formData.can_create && formData.can_read && formData.can_update && formData.can_delete
  }, [formData.can_create, formData.can_read, formData.can_update, formData.can_delete])

  // Handler untuk toggle all permissions
  const handleToggleAll = (checked: boolean) => {
    setFormData({
      ...formData,
      can_create: checked,
      can_read: checked,
      can_update: checked,
      can_delete: checked,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (!formData.page_id) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Page wajib dipilih',
        })
        setLoading(false)
        return
      }

      if (!formData.can_create && !formData.can_read && !formData.can_update && !formData.can_delete) {
        await Swal.fire({
          icon: 'warning',
          title: 'Perhatian',
          text: 'Minimal pilih satu permission (Create, Read, Update, atau Delete)',
        })
        setLoading(false)
        return
      }

      if (permission) {
        const updateData: PermissionUpdateRequest = {
          can_create: formData.can_create,
          can_read: formData.can_read,
          can_update: formData.can_update,
          can_delete: formData.can_delete,
        }
        await userManagementApi.updatePermission(permission.id, updateData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Permission berhasil diupdate',
          timer: 2000,
        })
      } else {
        await userManagementApi.createPermission(formData)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Permission berhasil dibuat',
          timer: 2000,
        })
      }

      onSuccess()
      onClose()
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.message || error.message || 'Gagal menyimpan permission',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          {permission ? 'Edit Permission' : 'Tambah Permission'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Page <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.page_id}
              onChange={(e) =>
                setFormData({ ...formData, page_id: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={!!pageId || loadingPages}
            >
              <option value={0}>Pilih Page</option>
              {pages && pages.length > 0 ? (
                pages.map((page) => (
                  <option key={page.id} value={page.id}>
                    {page.display_name} ({page.path})
                  </option>
                ))
              ) : (
                <option value={0} disabled>Memuat pages...</option>
              )}
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Permissions <span className="text-red-500">*</span>
            </label>
            <div className="space-y-2">
              {/* Select All Checkbox */}
              <label className="flex items-center pb-2 border-b border-gray-200">
                <input
                  type="checkbox"
                  checked={allPermissionsChecked}
                  onChange={(e) => handleToggleAll(e.target.checked)}
                  className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="ml-2 text-sm font-semibold text-gray-900">Select All</span>
              </label>
              
              {/* Individual Permission Checkboxes */}
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.can_create}
                  onChange={(e) =>
                    setFormData({ ...formData, can_create: e.target.checked })
                  }
                  className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="ml-2 text-sm text-gray-700">Create</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.can_read}
                  onChange={(e) =>
                    setFormData({ ...formData, can_read: e.target.checked })
                  }
                  className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="ml-2 text-sm text-gray-700">Read</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.can_update}
                  onChange={(e) =>
                    setFormData({ ...formData, can_update: e.target.checked })
                  }
                  className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="ml-2 text-sm text-gray-700">Update</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.can_delete}
                  onChange={(e) =>
                    setFormData({ ...formData, can_delete: e.target.checked })
                  }
                  className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="ml-2 text-sm text-gray-700">Delete</span>
              </label>
            </div>
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
              disabled={loading || loadingPages}
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

export default PermissionForm

