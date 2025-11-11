import React, { useState, useEffect } from 'react'
import { Role, RoleDetail, Page, Permission } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import RolePermissionCRUDMatrix from './RolePermissionCRUDMatrix'
import Swal from 'sweetalert2'

interface CRUDFlags {
  can_create: boolean
  can_read: boolean
  can_update: boolean
  can_delete: boolean
}

interface RolePermissionModalProps {
  role: Role
  onClose: () => void
  onSuccess: () => void
}

const RolePermissionModal: React.FC<RolePermissionModalProps> = ({
  role,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [pages, setPages] = useState<Page[]>([])
  const [pageCRUDPermissions, setPageCRUDPermissions] = useState<Map<number, CRUDFlags>>(
    new Map()
  )
  const [roleDetail, setRoleDetail] = useState<RoleDetail | null>(null)

  useEffect(() => {
    if (role?.id) {
      loadData()
    }
  }, [role?.id])

  const loadData = async () => {
    try {
      setLoadingData(true)
      const [pagesResponse, roleDetailResponse] = await Promise.all([
        userManagementApi.getPages(1, 100),
        userManagementApi.getRole(role.id, true),
      ])

      // Extract pages data dari paginated response
      const pagesData = pagesResponse.data || []
      setPages(pagesData)

      // Initialize CRUD permissions map dengan default false untuk semua pages
      const initialPermissions = new Map<number, CRUDFlags>()
      pagesData.forEach((page: Page) => {
        initialPermissions.set(page.id, {
          can_create: false,
          can_read: false,
          can_update: false,
          can_delete: false,
        })
      })

      // Populate dari role permissions yang sudah ada
      if (roleDetailResponse && 'permissions' in roleDetailResponse) {
        setRoleDetail(roleDetailResponse as RoleDetail)
        const rolePerms = (roleDetailResponse as RoleDetail).permissions || []
        
        // Group permissions by page_id
        const permissionsByPage = new Map<number, Permission[]>()
        rolePerms.forEach((perm: Permission) => {
          const pageId = perm.page_id
          if (!permissionsByPage.has(pageId)) {
            permissionsByPage.set(pageId, [])
          }
          permissionsByPage.get(pageId)!.push(perm)
        })

        // Untuk setiap page, merge CRUD flags dari semua permissions
        permissionsByPage.forEach((perms, pageId) => {
          const mergedFlags: CRUDFlags = {
            can_create: perms.some((p) => p.can_create),
            can_read: perms.some((p) => p.can_read),
            can_update: perms.some((p) => p.can_update),
            can_delete: perms.some((p) => p.can_delete),
          }
          initialPermissions.set(pageId, mergedFlags)
        })
      }

      setPageCRUDPermissions(initialPermissions)
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      console.error('Error loading permissions data:', error)
      await Swal.fire({
        icon: 'error',
        title: 'Gagal Memuat Data',
        text: error.response?.data?.detail || error.response?.data?.message || error.message || 'Gagal memuat data permissions. Silakan coba lagi.',
        confirmButtonText: 'OK',
      })
      // Tutup modal jika error saat load data
      onClose()
    } finally {
      setLoadingData(false)
    }
  }

  const handleCRUDChange = (pageId: number, crudFlags: CRUDFlags) => {
    const newPermissions = new Map(pageCRUDPermissions)
    newPermissions.set(pageId, crudFlags)
    setPageCRUDPermissions(newPermissions)
  }

  const handleSave = async () => {
    try {
      setLoading(true)

      // Convert Map to array format untuk API
      const pagePermissions = Array.from(pageCRUDPermissions.entries()).map(([pageId, flags]) => ({
        page_id: pageId,
        ...flags,
      }))

      await userManagementApi.assignRolePermissionsCRUD(role.id, {
        page_permissions: pagePermissions,
      })

      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Permissions berhasil di-assign ke role',
        timer: 2000,
      })

      onSuccess()
      onClose()
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      console.error('Error saving permissions:', error)
      await Swal.fire({
        icon: 'error',
        title: 'Gagal Menyimpan',
        text: error.response?.data?.detail || error.response?.data?.message || error.message || 'Gagal menyimpan permissions. Silakan coba lagi.',
        confirmButtonText: 'OK',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Manage Permissions untuk Role: {role.name}
        </h2>
        <p className="text-sm text-gray-600 mb-6">
          Edit CRUD permissions per halaman untuk role ini. Users dengan role ini akan otomatis mendapatkan permissions yang diatur.
        </p>

        <RolePermissionCRUDMatrix
          pages={pages}
          pageCRUDPermissions={pageCRUDPermissions}
          onCRUDChange={handleCRUDChange}
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

export default RolePermissionModal

