import React from 'react'
import { Page } from '../types'

interface PageListProps {
  pages: Page[]
  loading: boolean
  onEdit?: (page: Page) => void
  onDelete?: (page: Page) => void
}

const PageList: React.FC<PageListProps> = ({ pages, loading, onEdit, onDelete }) => {
  if (loading && pages.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 text-center text-gray-500">
          Memuat data...
        </div>
      </div>
    )
  }

  if (pages.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 text-center text-gray-500">
          Tidak ada data page
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
                Nama
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Path
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Display Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Order
              </th>
              {onEdit || onDelete ? (
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Aksi
                </th>
              ) : null}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {pages.map((page) => (
              <tr key={page.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {page.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {page.path}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {page.display_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {page.order}
                </td>
                {onEdit || onDelete ? (
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {onEdit && (
                      <button
                        onClick={() => onEdit(page)}
                        className="text-indigo-600 hover:text-indigo-900 mr-4"
                      >
                        Edit
                      </button>
                    )}
                    {onDelete && (
                      <button
                        onClick={() => onDelete(page)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Hapus
                      </button>
                    )}
                  </td>
                ) : null}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default PageList

