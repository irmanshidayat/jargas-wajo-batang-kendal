import React, { useState, useEffect, useMemo } from 'react'
import { Page, Permission } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import Swal from 'sweetalert2'
import PageList from '../components/PageList'
import PermissionForm from '../components/PermissionForm'
import PageFormModal from '../components/PageFormModal'
import { PageHeader, SearchBox } from '@/components/common'

const PermissionsManagementPage: React.FC = () => {
  const [pages, setPages] = useState<Page[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showPermissionForm, setShowPermissionForm] = useState(false)
  const [showPageForm, setShowPageForm] = useState(false)
  const [editingPermission, setEditingPermission] = useState<Permission | null>(null)
  const [selectedPageId, setSelectedPageId] = useState<number | undefined>(undefined)
  const [selectedPage, setSelectedPage] = useState<Page | null>(null)
  const [editingPage, setEditingPage] = useState<Page | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [pagesResponse, permissionsResponse] = await Promise.all([
        userManagementApi.getPages(1, 100),
        userManagementApi.getPermissions(1, 100),
      ])

      setPages(Array.isArray(pagesResponse.data) ? pagesResponse.data : pagesResponse.data || [])
      
      const allPerms = Array.isArray(permissionsResponse) 
        ? permissionsResponse 
        : (permissionsResponse as any)?.data || []
      setPermissions(allPerms)
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.message || 'Gagal memuat data permissions',
      })
    } finally {
      setLoading(false)
    }
  }

  // Search filtering is handled client-side via useMemo filteredPages

  const handleCreatePermission = (pageId?: number) => {
    setEditingPermission(null)
    setSelectedPageId(pageId)
    setShowPermissionForm(true)
  }

  const handleEditPermission = (permission: Permission) => {
    setEditingPermission(permission)
    setSelectedPageId(undefined)
    setShowPermissionForm(true)
  }

  const handleCreatePage = () => {
    setEditingPage(null)
    setShowPageForm(true)
  }

  const handleEditPage = (page: Page) => {
    setEditingPage(page)
    setShowPageForm(true)
  }

  const handleDeletePage = async (page: Page) => {
    const result = await Swal.fire({
      title: 'Hapus Page?',
      text: `Apakah Anda yakin ingin menghapus page "${page.display_name}"?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Ya, Hapus!',
      cancelButtonText: 'Batal',
    })

    if (result.isConfirmed) {
      try {
        setLoading(true)
        await userManagementApi.deletePage(page.id)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Page berhasil dihapus',
          timer: 2000,
        })
        loadData()
      } catch (error: any) {
        // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
        if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
          return
        }
        
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.message || 'Gagal menghapus page',
        })
      } finally {
        setLoading(false)
      }
    }
  }

  const handleDeletePermission = async (permission: Permission) => {
    const result = await Swal.fire({
      title: 'Hapus Permission?',
      text: `Apakah Anda yakin ingin menghapus permission ini?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Ya, Hapus!',
      cancelButtonText: 'Batal',
    })

    if (result.isConfirmed) {
      try {
        setLoading(true)
        await userManagementApi.deletePermission(permission.id)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Permission berhasil dihapus',
          timer: 2000,
        })
        loadData()
      } catch (error: any) {
        // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
        if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
          return
        }
        
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.message || 'Gagal menghapus permission',
        })
      } finally {
        setLoading(false)
      }
    }
  }

  const handlePermissionFormSuccess = () => {
    loadData()
  }

  const handlePageFormSuccess = () => {
    loadData()
    setShowPageForm(false)
    setEditingPage(null)
  }

  const filteredPages = useMemo(() => {
    if (!searchTerm) return pages
    const term = searchTerm.toLowerCase()
    return pages.filter(
      (page) =>
        page.name.toLowerCase().includes(term) ||
        page.path.toLowerCase().includes(term) ||
        page.display_name.toLowerCase().includes(term)
    )
  }, [pages, searchTerm])

  // Group permissions by page for display
  const permissionsByPage = useMemo(() => {
    return filteredPages.map((page) => {
      const pagePermissions = permissions.filter((p) => p.page_id === page.id)
      return { page, permissions: pagePermissions }
    })
  }, [filteredPages, permissions])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <PageHeader
        title="Manajemen Permissions"
        description="Kelola pages dan permissions, assign ke roles atau users"
        actionButton={
          <div className="flex gap-2">
            <button
              onClick={handleCreatePage}
              className="px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 font-semibold transition-colors shadow-md"
            >
              + Tambah Page
            </button>
            <button
              onClick={() => handleCreatePermission()}
              className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-400 font-semibold transition-colors shadow-md"
            >
              + Tambah Permission
            </button>
          </div>
        }
      />

      {/* Search */}
      <SearchBox
        value={searchTerm}
        onChange={setSearchTerm}
        placeholder="Cari berdasarkan nama page, path, atau display name..."
      />

      {/* Pages List */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Daftar Pages</h2>
        <PageList
          pages={filteredPages}
          loading={loading}
          onEdit={handleEditPage}
          onDelete={handleDeletePage}
        />
      </div>

      {/* Permissions Matrix */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Permissions Matrix</h2>
          <button
            onClick={() => handleCreatePermission()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold transition-colors"
          >
            + Tambah Permission
          </button>
        </div>
        {permissionsByPage.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {loading ? 'Memuat data...' : 'Belum ada pages atau permissions. Silakan buat page terlebih dahulu.'}
          </div>
        ) : (
          <div className="space-y-6">
            {permissionsByPage.map(({ page, permissions: pagePerms }) => (
              <div key={page.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">{page.display_name}</h3>
                  <button
                    onClick={() => handleCreatePermission(page.id)}
                    className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    + Tambah Permission
                  </button>
                </div>
                {pagePerms.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                            Create
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                            Read
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                            Update
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                            Delete
                          </th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-gray-700 uppercase">
                            Aksi
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {pagePerms.map((perm) => (
                          <tr key={perm.id} className="hover:bg-gray-50">
                            <td className="px-4 py-2 text-sm">
                              {perm.can_create ? '✓' : '-'}
                            </td>
                            <td className="px-4 py-2 text-sm">
                              {perm.can_read ? '✓' : '-'}
                            </td>
                            <td className="px-4 py-2 text-sm">
                              {perm.can_update ? '✓' : '-'}
                            </td>
                            <td className="px-4 py-2 text-sm">
                              {perm.can_delete ? '✓' : '-'}
                            </td>
                            <td className="px-4 py-2 text-right text-sm">
                              <button
                                onClick={() => handleEditPermission(perm)}
                                className="text-indigo-600 hover:text-indigo-900 mr-4"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleDeletePermission(perm)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Hapus
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 py-4 text-center">Belum ada permissions untuk page ini</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      {showPermissionForm && (
        <PermissionForm
          permission={editingPermission}
          pageId={selectedPageId}
          onClose={() => {
            setShowPermissionForm(false)
            setEditingPermission(null)
            setSelectedPageId(undefined)
          }}
          onSuccess={handlePermissionFormSuccess}
        />
      )}

      {showPageForm && (
        <PageFormModal
          page={editingPage}
          onClose={() => {
            setShowPageForm(false)
            setEditingPage(null)
          }}
          onSuccess={handlePageFormSuccess}
        />
      )}
    </div>
  )
}

export default PermissionsManagementPage
