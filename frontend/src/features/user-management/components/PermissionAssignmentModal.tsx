import React, { useState, useEffect } from 'react'
import { User, Page, Permission } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import PermissionMatrix from './PermissionMatrix'
import Swal from 'sweetalert2'

interface PermissionAssignmentModalProps {
  user: User
  onClose: () => void
  onSuccess: () => void
}

const PermissionAssignmentModal: React.FC<PermissionAssignmentModalProps> = ({
  user,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [pages, setPages] = useState<Page[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [selectedPermissionIds, setSelectedPermissionIds] = useState<number[]>([])
  const [userPermissions, setUserPermissions] = useState<Permission[]>([])

  useEffect(() => {
    loadData()
  }, [user])

  // Handler untuk memastikan selectedPermissionIds selalu unik
  const handlePermissionChange = (permissionIds: number[]) => {
    // Deduplicate untuk memastikan tidak ada duplicate
    const uniqueIds = Array.from(new Set(permissionIds))
    setSelectedPermissionIds(uniqueIds)
  }

  const loadData = async () => {
    try {
      setLoadingData(true)
      const [pagesResponse, permissionsResponse, userPermsResponse] = await Promise.all([
        userManagementApi.getPages(1, 100),
        userManagementApi.getPermissions(1, 100),
        userManagementApi.getUserPermissions(user.id),
      ])

      setPages(Array.isArray(pagesResponse.data) ? pagesResponse.data : pagesResponse.data || [])
      
      const allPerms = Array.isArray(permissionsResponse) 
        ? permissionsResponse 
        : (permissionsResponse as any)?.data || []
      setPermissions(allPerms)
      
      const userPerms = Array.isArray(userPermsResponse) ? userPermsResponse : []
      setUserPermissions(userPerms)
      setSelectedPermissionIds(userPerms.map((p) => p.id))
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Gagal memuat data permissions',
      })
    } finally {
      setLoadingData(false)
    }
  }

  const handleSave = async () => {
    try {
      setLoading(true)
      
      // Deduplicate permission_ids untuk menghindari duplicate constraint violation
      const uniquePermissionIds = Array.from(new Set(selectedPermissionIds))
      
      await userManagementApi.assignUserPermissions(user.id, {
        permission_ids: uniquePermissionIds,
      })

      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Permissions berhasil di-assign ke user',
        timer: 2000,
      })

      onSuccess()
      onClose()
    } catch (error: any) {
      // Extract error message dari response
      const errorMessage = 
        error.response?.data?.message || 
        error.response?.data?.detail || 
        error.message || 
        'Gagal menyimpan permissions'
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: errorMessage,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Assign Permissions untuk {user.name}
        </h2>
        <p className="text-sm text-gray-600 mb-6">
          Pilih permissions yang akan diberikan ke user ini. Permissions ini akan override permissions dari role.
        </p>

        <PermissionMatrix
          userId={user.id}
          pages={pages}
          permissions={permissions}
          selectedPermissionIds={selectedPermissionIds}
          onPermissionChange={handlePermissionChange}
          isLoading={loadingData}
        />

        <div className="flex justify-end space-x-4 pt-6 mt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            disabled={loading}
          >
            Batal
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={loading || loadingData}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Menyimpan...' : 'Simpan Permissions'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default PermissionAssignmentModal

