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

  // Group permissions by page
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
                
                return (
                  <React.Fragment key={page.id}>
                    {pagePerms.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-3 text-sm text-gray-500">
                          {page.display_name} - Belum ada permissions
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
                    ) : (
                      pagePerms.map((perm, index) => (
                        <tr key={perm.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                            {page.display_name}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {perm.can_create ? (
                              <input
                                type="checkbox"
                                checked={localSelectedIds.has(perm.id)}
                                onChange={() => handlePermissionToggle(perm.id)}
                                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                              />
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {perm.can_read ? (
                              <input
                                type="checkbox"
                                checked={localSelectedIds.has(perm.id)}
                                onChange={() => handlePermissionToggle(perm.id)}
                                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                              />
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {perm.can_update ? (
                              <input
                                type="checkbox"
                                checked={localSelectedIds.has(perm.id)}
                                onChange={() => handlePermissionToggle(perm.id)}
                                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                              />
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {perm.can_delete ? (
                              <input
                                type="checkbox"
                                checked={localSelectedIds.has(perm.id)}
                                onChange={() => handlePermissionToggle(perm.id)}
                                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                              />
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {index === 0 && (
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
                            )}
                            {index > 0 && <span className="text-gray-400">-</span>}
                          </td>
                        </tr>
                      ))
                    )}
                  </React.Fragment>
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

