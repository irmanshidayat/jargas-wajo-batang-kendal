import React, { useState, useEffect, useMemo } from 'react'
import { User } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import Swal from 'sweetalert2'
import UserList from '../components/UserList'
import UserForm from '../components/UserForm'
import PermissionAssignmentModal from '../components/PermissionAssignmentModal'
import { Pagination, PageHeader, SearchBox } from '@/components/common'
import { useSearchDebounce } from '@/hooks/useSearchDebounce'

const UsersManagementPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const [limit] = useState(10)
  const [total, setTotal] = useState(0)
  const [showUserForm, setShowUserForm] = useState(false)
  const [showPermissionModal, setShowPermissionModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [editingUser, setEditingUser] = useState<User | null>(null)

  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(total / limit))
  }, [total, limit])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const response = await userManagementApi.getUsers(page, limit)
      setUsers(response.data || [])
      setTotal(response.total || 0)
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.message || error.message || 'Gagal memuat daftar users',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [page])

  useSearchDebounce({
    searchTerm,
    currentPage: page,
    onSearch: loadUsers,
  })

  useEffect(() => {
    if (searchTerm && page !== 1) {
      setPage(1)
    }
  }, [searchTerm])

  const handleCreateUser = () => {
    setEditingUser(null)
    setShowUserForm(true)
  }

  const handleEditUser = (user: User) => {
    setEditingUser(user)
    setShowUserForm(true)
  }

  const handleAssignRole = async (user: User) => {
    // Simple role assignment - just open a form with role selector
    // For now, we'll use UserForm modal with just role selection
    setEditingUser(user)
    setShowUserForm(true)
  }

  const handleAssignPermissions = (user: User) => {
    setSelectedUser(user)
    setShowPermissionModal(true)
  }

  const handleDeleteUser = async (user: User) => {
    if (user.is_superuser) {
      await Swal.fire({
        icon: 'warning',
        title: 'Tidak Bisa Dihapus',
        text: 'Superuser tidak dapat dihapus',
      })
      return
    }

    const result = await Swal.fire({
      title: 'Hapus User?',
      text: `Apakah Anda yakin ingin menghapus user "${user.name}"?`,
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
        await userManagementApi.deleteUser(user.id)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'User berhasil dihapus',
          timer: 2000,
        })
        loadUsers()
      } catch (error: any) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.message || 'Gagal menghapus user',
        })
      } finally {
        setLoading(false)
      }
    }
  }

  const handleUserFormSuccess = () => {
    loadUsers()
  }

  const handlePermissionModalSuccess = () => {
    loadUsers()
  }

  const filteredUsers = useMemo(() => {
    if (!searchTerm) return users
    const term = searchTerm.toLowerCase()
    return users.filter(
      (user) =>
        user.name.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term) ||
        user.role?.name?.toLowerCase().includes(term)
    )
  }, [users, searchTerm])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <PageHeader
        title="Manajemen User"
        description="Kelola users, assign roles, dan permissions"
        actionButton={
          <button
            onClick={handleCreateUser}
            className="px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 font-semibold transition-colors shadow-md"
          >
            + Tambah User
          </button>
        }
      />

      {/* Search */}
      <SearchBox
        value={searchTerm}
        onChange={setSearchTerm}
        placeholder="Cari berdasarkan nama, email, atau role..."
      />

      {/* Table */}
      <UserList
        users={filteredUsers}
        loading={loading}
        onEdit={handleEditUser}
        onAssignRole={handleAssignRole}
        onAssignPermissions={handleAssignPermissions}
        onDelete={handleDeleteUser}
      />

      {/* Pagination */}
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
        loading={loading}
      />

      {/* Modals */}
      {showUserForm && (
        <UserForm
          user={editingUser}
          onClose={() => {
            setShowUserForm(false)
            setEditingUser(null)
          }}
          onSuccess={handleUserFormSuccess}
        />
      )}

      {showPermissionModal && selectedUser && (
        <PermissionAssignmentModal
          user={selectedUser}
          onClose={() => {
            setShowPermissionModal(false)
            setSelectedUser(null)
          }}
          onSuccess={handlePermissionModalSuccess}
        />
      )}
    </div>
  )
}

export default UsersManagementPage
