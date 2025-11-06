import React, { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { Header, Sidebar, Footer } from './index'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { refreshUserPermissions } from '@/store/slices/authSlice'

const Layout: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const dispatch = useAppDispatch()
  const { isAuthenticated, user } = useAppSelector((state) => state.auth)

  // Auto-refresh permissions saat aplikasi dibuka (hanya sekali saat mount)
  useEffect(() => {
    if (isAuthenticated && user) {
      // Refresh permissions untuk memastikan menu sesuai dengan role terbaru
      dispatch(refreshUserPermissions()).catch((error) => {
        // Silent fail - tidak perlu notify user jika refresh gagal
        console.warn('Auto-refresh permissions gagal:', error)
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Hanya sekali saat mount - dispatch dan state lainnya tidak perlu di-dependency

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  const closeSidebar = () => {
    setIsSidebarOpen(false)
  }

  return (
    <div className="min-h-screen flex bg-slate-50 overflow-x-hidden">
      <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />
      <div className="flex flex-col flex-1 lg:ml-64 overflow-x-hidden w-full max-w-full">
        <Header onToggleSidebar={toggleSidebar} />
        <main className="flex-1 pt-6 pb-6 px-6 md:px-8 lg:px-10 bg-slate-50 overflow-x-hidden w-full max-w-full">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  )
}

export default Layout

