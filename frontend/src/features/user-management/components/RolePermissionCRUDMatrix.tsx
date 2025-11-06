import React, { useState, useEffect } from 'react'
import { Page } from '../types'

interface CRUDFlags {
  can_create: boolean
  can_read: boolean
  can_update: boolean
  can_delete: boolean
}

interface RolePermissionCRUDMatrixProps {
  pages: Page[]
  pageCRUDPermissions: Map<number, CRUDFlags>
  onCRUDChange: (pageId: number, crudFlags: CRUDFlags) => void
  isLoading?: boolean
}

const RolePermissionCRUDMatrix: React.FC<RolePermissionCRUDMatrixProps> = ({
  pages,
  pageCRUDPermissions,
  onCRUDChange,
  isLoading = false,
}) => {
  const [localPermissions, setLocalPermissions] = useState<Map<number, CRUDFlags>>(
    new Map(pageCRUDPermissions)
  )

  useEffect(() => {
    setLocalPermissions(new Map(pageCRUDPermissions))
  }, [pageCRUDPermissions])

  const handleCRUDToggle = (pageId: number, field: keyof CRUDFlags, value: boolean) => {
    const currentFlags = localPermissions.get(pageId) || {
      can_create: false,
      can_read: false,
      can_update: false,
      can_delete: false,
    }

    const newFlags = {
      ...currentFlags,
      [field]: value,
    }

    const newPermissions = new Map(localPermissions)
    newPermissions.set(pageId, newFlags)
    setLocalPermissions(newPermissions)
    onCRUDChange(pageId, newFlags)
  }

  const handleToggleAll = (pageId: number, checked: boolean) => {
    const newFlags: CRUDFlags = {
      can_create: checked,
      can_read: checked,
      can_update: checked,
      can_delete: checked,
    }

    const newPermissions = new Map(localPermissions)
    newPermissions.set(pageId, newFlags)
    setLocalPermissions(newPermissions)
    onCRUDChange(pageId, newFlags)
  }

  const getPageFlags = (pageId: number): CRUDFlags => {
    return localPermissions.get(pageId) || {
      can_create: false,
      can_read: false,
      can_update: false,
      can_delete: false,
    }
  }

  const isAllChecked = (pageId: number): boolean => {
    const flags = getPageFlags(pageId)
    return flags.can_create && flags.can_read && flags.can_update && flags.can_delete
  }

  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Memuat permissions...</div>
  }

  if (pages.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        Belum ada pages. Silakan buat page terlebih dahulu.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 bg-white rounded-lg shadow">
        <thead className="bg-gradient-to-r from-indigo-50 to-purple-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
              Halaman
            </th>
            <th className="px-4 py-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wider">
              <span className="inline-flex items-center gap-1">
                Select All
              </span>
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
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {pages.map((page) => {
            const flags = getPageFlags(page.id)
            const allChecked = isAllChecked(page.id)

            return (
              <tr key={page.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                  {page.display_name}
                </td>
                <td className="px-4 py-3 text-center">
                  <input
                    type="checkbox"
                    checked={allChecked}
                    onChange={(e) => handleToggleAll(page.id, e.target.checked)}
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                    title="Select All untuk halaman ini"
                  />
                </td>
                <td className="px-4 py-3 text-center">
                  <input
                    type="checkbox"
                    checked={flags.can_create}
                    onChange={(e) =>
                      handleCRUDToggle(page.id, 'can_create', e.target.checked)
                    }
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                </td>
                <td className="px-4 py-3 text-center">
                  <input
                    type="checkbox"
                    checked={flags.can_read}
                    onChange={(e) =>
                      handleCRUDToggle(page.id, 'can_read', e.target.checked)
                    }
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                </td>
                <td className="px-4 py-3 text-center">
                  <input
                    type="checkbox"
                    checked={flags.can_update}
                    onChange={(e) =>
                      handleCRUDToggle(page.id, 'can_update', e.target.checked)
                    }
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                </td>
                <td className="px-4 py-3 text-center">
                  <input
                    type="checkbox"
                    checked={flags.can_delete}
                    onChange={(e) =>
                      handleCRUDToggle(page.id, 'can_delete', e.target.checked)
                    }
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default RolePermissionCRUDMatrix

