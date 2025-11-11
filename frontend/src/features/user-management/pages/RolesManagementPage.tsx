import React, { useState, useEffect, useMemo } from 'react'
import { Role } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import Swal from 'sweetalert2'
import RoleList from '../components/RoleList'
import RoleForm from '../components/RoleForm'
import RolePermissionModal from '../components/RolePermissionModal'
import { Pagination, PageHeader, SearchBox } from '@/components/common'
import { useSearchDebounce } from '@/hooks/useSearchDebounce'

const RolesManagementPage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const [limit] = useState(10)
  const [total, setTotal] = useState(0)
  const [showRoleForm, setShowRoleForm] = useState(false)
  const [showPermissionModal, setShowPermissionModal] = useState(false)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [editingRole, setEditingRole] = useState<Role | null>(null)

  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(total / limit))
  }, [total, limit])

  const loadRoles = async () => {
    try {
      setLoading(true)
      const response = await userManagementApi.getRoles(page, limit)
      setRoles(response.data || [])
      setTotal(response.total || 0)
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.message || 'Gagal memuat daftar roles',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRoles()
  }, [page])

  useSearchDebounce({
    searchTerm,
    currentPage: page,
    onSearch: loadRoles,
  })

  useEffect(() => {
    if (searchTerm && page !== 1) {
      setPage(1)
    }
  }, [searchTerm])

  const handleCreateRole = () => {
    setEditingRole(null)
    setShowRoleForm(true)
  }

  const handleEditRole = (role: Role) => {
    setEditingRole(role)
    setShowRoleForm(true)
  }

  const handleManagePermissions = (role: Role) => {
    setSelectedRole(role)
    setShowPermissionModal(true)
  }

  const handleDeleteRole = async (role: Role) => {
    const result = await Swal.fire({
      title: 'Hapus Role?',
      text: `Apakah Anda yakin ingin menghapus role "${role.name}"?`,
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
        await userManagementApi.deleteRole(role.id)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Role berhasil dihapus',
          timer: 2000,
        })
        loadRoles()
      } catch (error: any) {
        // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
        if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
          return
        }
        
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.message || 'Gagal menghapus role',
        })
      } finally {
        setLoading(false)
      }
    }
  }

  const handleRoleFormSuccess = () => {
    loadRoles()
  }

  const handlePermissionModalSuccess = () => {
    loadRoles()
  }

  const filteredRoles = useMemo(() => {
    if (!searchTerm) return roles
    const term = searchTerm.toLowerCase()
    return roles.filter(
      (role) =>
        role.name.toLowerCase().includes(term) ||
        role.description?.toLowerCase().includes(term)
    )
  }, [roles, searchTerm])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <PageHeader
        title="Manajemen Role"
        description="Kelola roles dan assign permissions"
        actionButton={
          <button
            onClick={handleCreateRole}
            className="px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 font-semibold transition-colors shadow-md"
          >
            + Tambah Role
          </button>
        }
      />

      {/* Search */}
      <SearchBox
        value={searchTerm}
        onChange={setSearchTerm}
        placeholder="Cari berdasarkan nama atau deskripsi role..."
      />

      {/* Table */}
      <RoleList
        roles={filteredRoles}
        loading={loading}
        onEdit={handleEditRole}
        onManagePermissions={handleManagePermissions}
        onDelete={handleDeleteRole}
      />

      {/* Pagination */}
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
        loading={loading}
      />

      {/* Modals */}
      {showRoleForm && (
        <RoleForm
          role={editingRole}
          onClose={() => {
            setShowRoleForm(false)
            setEditingRole(null)
          }}
          onSuccess={handleRoleFormSuccess}
        />
      )}

      {showPermissionModal && selectedRole && (
        <RolePermissionModal
          role={selectedRole}
          onClose={() => {
            setShowPermissionModal(false)
            setSelectedRole(null)
          }}
          onSuccess={handlePermissionModalSuccess}
        />
      )}
    </div>
  )
}

export default RolesManagementPage
