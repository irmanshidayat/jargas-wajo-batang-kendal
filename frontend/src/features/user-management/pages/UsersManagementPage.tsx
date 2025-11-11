import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { User } from '../types'
import { userManagementApi } from '../services/userManagementApi'
import Swal from 'sweetalert2'
import UserList from '../components/UserList'
import UserForm from '../components/UserForm'
import PermissionAssignmentModal from '../components/PermissionAssignmentModal'
import { Pagination, PageHeader, SearchBox } from '@/components/common'
import { useSearchDebounce } from '@/hooks/useSearchDebounce'
import { useAppSelector } from '@/store/hooks'
import { isSuperuser } from '@/utils/auth'

const UsersManagementPage: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth)
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

  // Check if user is superuser menggunakan utility function
  // Note: PrivateRoute sudah handle access control, jadi tidak perlu redirect manual
  const userIsSuperuser = useMemo(() => isSuperuser(user), [user])

  const loadUsers = useCallback(async () => {
    // Only load if user is superuser
    if (!userIsSuperuser) return

    try {
      setLoading(true)
      const response = await userManagementApi.getUsers(page, limit)
      setUsers(response.data || [])
      setTotal(response.total || 0)
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      const errorMessage = error.response?.data?.message || error.message || 'Gagal memuat daftar users'
      
      // Handle error (PrivateRoute sudah handle access control)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: errorMessage,
      })
    } finally {
      setLoading(false)
    }
  }, [userIsSuperuser, page, limit])

  useEffect(() => {
    if (userIsSuperuser) {
      loadUsers()
    }
  }, [userIsSuperuser, loadUsers])

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
        // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
        if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
          return
        }
        
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

  // Don't render if not superuser
  // Note: PrivateRoute sudah handle redirect, ini hanya untuk safety
  if (!userIsSuperuser) {
    return null
  }

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
