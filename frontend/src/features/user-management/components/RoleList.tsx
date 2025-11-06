import React from 'react'
import { Role } from '../types'

interface RoleListProps {
  roles: Role[]
  loading: boolean
  onEdit: (role: Role) => void
  onManagePermissions: (role: Role) => void
  onDelete: (role: Role) => void
}

const RoleList: React.FC<RoleListProps> = ({
  roles,
  loading,
  onEdit,
  onManagePermissions,
  onDelete,
}) => {
  if (loading && roles.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 text-center text-gray-500">
          Memuat data...
        </div>
      </div>
    )
  }

  if (roles.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 text-center text-gray-500">
          Tidak ada data role
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gradient-to-r from-indigo-50 to-purple-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Nama Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Deskripsi
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                Aksi
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {roles.map((role) => (
              <tr key={role.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {role.name}
                </td>
                <td className="px-6 py-4 text-sm text-gray-700">
                  {role.description || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => onEdit(role)}
                      className="text-indigo-600 hover:text-indigo-900"
                      title="Edit"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onManagePermissions(role)}
                      className="text-purple-600 hover:text-purple-900"
                      title="Manage Permissions"
                    >
                      Permissions
                    </button>
                    <button
                      onClick={() => onDelete(role)}
                      className="text-red-600 hover:text-red-900"
                      title="Delete"
                    >
                      Hapus
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default RoleList

