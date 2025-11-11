import React, { useState } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { logout, refreshUserPermissions } from '@/store/slices/authSlice'
import { clearProject } from '@/store/slices/projectSlice'
import { useNavigate } from 'react-router-dom'
import Swal from 'sweetalert2'
import { isSuperuser } from '@/utils/auth'

interface HeaderProps {
  onToggleSidebar: () => void
}

const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)
  const { currentProject } = useAppSelector((state) => state.project)

  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleSwitchProject = () => {
    // Clear project terlebih dahulu agar bisa mengakses halaman select-project
    dispatch(clearProject())
    navigate('/select-project')
  }

  const handleRefreshPermissions = async () => {
    try {
      setIsRefreshing(true)
      await dispatch(refreshUserPermissions()).unwrap()
      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Permissions berhasil di-refresh',
        timer: 1500,
        showConfirmButton: false,
      })
    } catch (error: any) {
      // Skip canceled errors - tidak perlu tampilkan error untuk request yang di-cancel
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        return
      }
      
      await Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.message || 'Gagal refresh permissions',
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleLogout = async () => {
    const result = await Swal.fire({
      title: 'Konfirmasi Logout',
      text: 'Apakah Anda yakin ingin logout?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Ya, Logout',
      cancelButtonText: 'Batal',
      confirmButtonColor: '#ef4444',
    })

    if (result.isConfirmed) {
      try {
        await dispatch(logout()).unwrap()
        navigate('/login')
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Anda telah logout',
          timer: 1500,
          showConfirmButton: false,
        })
      } catch (error) {
        await Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Gagal melakukan logout',
        })
      }
    }
  }

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50 border-b border-slate-200 w-full">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            {/* Hamburger Menu Button - Visible on tablet and mobile */}
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500"
              aria-label="Toggle menu"
            >
              <svg
                className="w-6 h-6 text-slate-700"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
            <h1 className="text-xl font-bold text-slate-900">Jargas APBN</h1>
          </div>
          {isAuthenticated && user && (
            <div className="flex items-center gap-3">
              {currentProject && (
                <div 
                  onClick={handleSwitchProject}
                  className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-indigo-50 rounded-lg border border-indigo-200 cursor-pointer hover:bg-indigo-100 transition-colors"
                  title="Ganti Project"
                >
                  <div className="w-2 h-2 bg-indigo-600 rounded-full"></div>
                  <span className="text-sm font-medium text-indigo-900">{currentProject.name}</span>
                  <div className="ml-1 text-indigo-600">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                    </svg>
                  </div>
                </div>
              )}
              <button
                onClick={handleRefreshPermissions}
                disabled={isRefreshing}
                className="p-2 rounded-lg hover:bg-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Refresh Permissions"
                aria-label="Refresh Permissions"
              >
                <svg
                  className={`w-5 h-5 text-slate-700 ${isRefreshing ? 'animate-spin' : ''}`}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-500 rounded-full flex items-center justify-center text-white font-semibold shadow-md">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="hidden md:block">
                  <p className="text-sm font-medium text-slate-900">{user.name}</p>
                  <p className="text-xs text-slate-500">
                    {isSuperuser(user) ? 'Superuser' : (user.role?.name || 'User')}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gradient-to-r from-red-500 to-rose-500 text-white rounded-lg hover:from-red-600 hover:to-rose-600 transition-all shadow-md hover:shadow-lg text-sm font-medium"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
