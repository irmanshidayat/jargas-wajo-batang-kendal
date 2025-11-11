import React, { useState, useEffect, useRef } from 'react'
import { Page, Permission } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import Swal from 'sweetalert2'

interface PermissionMatrixProps {
  userId: number
  pages: Page[]
  permissions: Permission[]
  selectedPermissionIds: number[]
  onPermissionChange: (permissionIds: number[]) => void
  isLoading?: boolean
}

const PermissionMatrix: React.FC<PermissionMatrixProps> = ({
  userId,
  pages,
  permissions,
  selectedPermissionIds,
  onPermissionChange,
  isLoading = false,
}) => {
  const [localSelectedIds, setLocalSelectedIds] = useState<Set<number>>(
    new Set(selectedPermissionIds)
  )
  const [userMenuPreferences, setUserMenuPreferences] = useState<Map<number, boolean>>(new Map())
  const [updatingPages, setUpdatingPages] = useState<Set<number>>(new Set())
  
  // Ref untuk mencegah duplicate calls
  const isFetchingPreferencesRef = useRef(false)
  const lastFetchedUserIdRef = useRef<number | null>(null)

  useEffect(() => {
    setLocalSelectedIds(new Set(selectedPermissionIds))
  }, [selectedPermissionIds])

  // Fetch user menu preferences - dengan guard untuk prevent duplicate calls
  useEffect(() => {
    const fetchPreferences = async () => {
      if (!userId) return
      
      // Skip jika sedang fetching untuk user yang sama
      if (isFetchingPreferencesRef.current && lastFetchedUserIdRef.current === userId) {
        return
      }
      
      // Skip jika sudah pernah fetch untuk user ini
      if (lastFetchedUserIdRef.current === userId) {
        return
      }
      
      try {
        isFetchingPreferencesRef.current = true
        lastFetchedUserIdRef.current = userId
        const preferences = await userManagementApi.getUserMenuPreferences(userId)
        const preferencesMap = new Map<number, boolean>()
        preferences.forEach(pref => {
          preferencesMap.set(pref.page_id, pref.show_in_menu)
        })
        setUserMenuPreferences(preferencesMap)
      } catch (error: any) {
        console.error('Error fetching user menu preferences:', error)
        // Reset ref agar bisa retry
        lastFetchedUserIdRef.current = null
        // Default ke empty map (semua menu akan ditampilkan)
        setUserMenuPreferences(new Map())
      } finally {
        isFetchingPreferencesRef.current = false
      }
    }

    // Reset ref jika userId berubah
    if (lastFetchedUserIdRef.current !== userId) {
      lastFetchedUserIdRef.current = null
      isFetchingPreferencesRef.current = false
    }

    if (userId) {
      fetchPreferences()
    }
  }, [userId])

  const handlePermissionToggle = (permissionId: number) => {
    const newSelected = new Set(localSelectedIds)
    if (newSelected.has(permissionId)) {
      newSelected.delete(permissionId)
    } else {
      newSelected.add(permissionId)
    }
    setLocalSelectedIds(newSelected)
    onPermissionChange(Array.from(newSelected))
  }

  const handleShowInMenuToggle = async (pageId: number) => {
    const currentValue = userMenuPreferences.get(pageId) ?? true
    const newValue = !currentValue
    
    // Optimistic update
    setUserMenuPreferences(prev => {
      const newMap = new Map(prev)
      newMap.set(pageId, newValue)
      return newMap
    })
    setUpdatingPages(prev => new Set(prev).add(pageId))

    try {
      await userManagementApi.createOrUpdateUserMenuPreference(userId, {
        page_id: pageId,
        show_in_menu: newValue
      })
      
      // Success - update sudah dilakukan di optimistic update
    } catch (error: any) {
      // Revert on error
      setUserMenuPreferences(prev => {
        const newMap = new Map(prev)
        newMap.set(pageId, currentValue)
        return newMap
      })
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.message || error.message || 'Gagal mengupdate tampil di menu',
      })
    } finally {
      setUpdatingPages(prev => {
        const newSet = new Set(prev)
        newSet.delete(pageId)
        return newSet
      })
    }
  }

  // Calculate CRUD status for each page based on selected permissions
  const getPageCRUDStatus = (pageId: number) => {
    const pagePermissions = permissions.filter((p) => p.page_id === pageId)
    const selectedPagePermissions = pagePermissions.filter((p) => localSelectedIds.has(p.id))
    
    return {
      can_create: selectedPagePermissions.some((p) => p.can_create),
      can_read: selectedPagePermissions.some((p) => p.can_read),
      can_update: selectedPagePermissions.some((p) => p.can_update),
      can_delete: selectedPagePermissions.some((p) => p.can_delete),
    }
  }

  // Handle CRUD toggle for a specific page
  const handleCRUDToggle = (pageId: number, crudType: 'can_create' | 'can_read' | 'can_update' | 'can_delete', value: boolean) => {
    const pagePermissions = permissions.filter((p) => p.page_id === pageId)
    const currentStatus = getPageCRUDStatus(pageId)
    const newStatus = { ...currentStatus, [crudType]: value }
    
    const newSelected = new Set(localSelectedIds)
    
    if (value) {
      // Enabling CRUD: Find permission that matches the new status
      // First try exact match
      let targetPermission = pagePermissions.find(
        (p) =>
          p.can_create === newStatus.can_create &&
          p.can_read === newStatus.can_read &&
          p.can_update === newStatus.can_update &&
          p.can_delete === newStatus.can_delete
      )
      
      // If exact match not found, find permission that has the required flag and is closest to new status
      if (!targetPermission) {
        // Find permissions that have the required flag
        const candidates = pagePermissions.filter((p) => p[crudType] === true)
        
        // Find the one that matches most of the other flags
        targetPermission = candidates.find((p) => {
          const matches = 
            (p.can_create === newStatus.can_create || !newStatus.can_create) &&
            (p.can_read === newStatus.can_read || !newStatus.can_read) &&
            (p.can_update === newStatus.can_update || !newStatus.can_update) &&
            (p.can_delete === newStatus.can_delete || !newStatus.can_delete)
          return matches
        })
        
        // If still not found, use the first candidate
        if (!targetPermission && candidates.length > 0) {
          targetPermission = candidates[0]
        }
      }
      
      // Remove all current permissions for this page
      const selectedPagePermIds = pagePermissions
        .filter((p) => localSelectedIds.has(p.id))
        .map((p) => p.id)
      selectedPagePermIds.forEach((id) => newSelected.delete(id))
      
      // Add the target permission
      if (targetPermission) {
        newSelected.add(targetPermission.id)
      }
    } else {
      // Disabling CRUD: Remove all permissions that have this flag
      const permissionsToRemove = pagePermissions
        .filter((p) => p[crudType] === true && localSelectedIds.has(p.id))
        .map((p) => p.id)
      
      permissionsToRemove.forEach((id) => newSelected.delete(id))
      
      // If there are still selected permissions, keep them
      // Otherwise, try to find a permission that matches the new status (without the disabled flag)
      const remainingSelected = pagePermissions.filter((p) => newSelected.has(p.id))
      if (remainingSelected.length === 0) {
        // Try to find a permission that matches the new status
        const targetPermission = pagePermissions.find(
          (p) =>
            p.can_create === newStatus.can_create &&
            p.can_read === newStatus.can_read &&
            p.can_update === newStatus.can_update &&
            p.can_delete === newStatus.can_delete
        )
        
        if (targetPermission) {
          newSelected.add(targetPermission.id)
        }
      }
    }
    
    setLocalSelectedIds(newSelected)
    onPermissionChange(Array.from(newSelected))
  }

  // Group permissions by page - one row per page
  const permissionsByPage = pages.map((page) => {
    const pagePermissions = permissions.filter((p) => p.page_id === page.id)
    return { page, permissions: pagePermissions }
  })

  return (
    <div className="space-y-4">
      {isLoading ? (
        <div className="text-center py-8 text-gray-500">Memuat permissions...</div>
      ) : permissionsByPage.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Belum ada pages atau permissions. Silakan buat page dan permission terlebih dahulu.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 bg-white rounded-lg shadow">
            <thead className="bg-gradient-to-r from-indigo-50 to-purple-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Halaman
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Create
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Read
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Update
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Delete
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Tampil di Menu
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {permissionsByPage.map(({ page, permissions: pagePerms }) => {
                const showInMenu = userMenuPreferences.get(page.id) ?? true
                const isUpdating = updatingPages.has(page.id)
                const crudStatus = getPageCRUDStatus(page.id)
                
                // Check if page has any permissions available
                const hasPermissions = pagePerms.length > 0
                
                return (
                  <tr key={page.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                      {page.display_name}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {hasPermissions && pagePerms.some((p) => p.can_create) ? (
                        <input
                          type="checkbox"
                          checked={crudStatus.can_create}
                          onChange={(e) => handleCRUDToggle(page.id, 'can_create', e.target.checked)}
                          className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                        />
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {hasPermissions && pagePerms.some((p) => p.can_read) ? (
                        <input
                          type="checkbox"
                          checked={crudStatus.can_read}
                          onChange={(e) => handleCRUDToggle(page.id, 'can_read', e.target.checked)}
                          className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                        />
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {hasPermissions && pagePerms.some((p) => p.can_update) ? (
                        <input
                          type="checkbox"
                          checked={crudStatus.can_update}
                          onChange={(e) => handleCRUDToggle(page.id, 'can_update', e.target.checked)}
                          className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                        />
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {hasPermissions && pagePerms.some((p) => p.can_delete) ? (
                        <input
                          type="checkbox"
                          checked={crudStatus.can_delete}
                          onChange={(e) => handleCRUDToggle(page.id, 'can_delete', e.target.checked)}
                          className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                        />
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={showInMenu}
                          onChange={() => handleShowInMenuToggle(page.id)}
                          disabled={isUpdating}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600 disabled:opacity-50"></div>
                      </label>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default PermissionMatrix

