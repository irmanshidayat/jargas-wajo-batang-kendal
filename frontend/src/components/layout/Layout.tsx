import React, { useState, useEffect, useRef } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { Header, Sidebar, Footer } from './index'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { refreshUserPermissions } from '@/store/slices/authSlice'

const Layout: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const dispatch = useAppDispatch()
  const { isAuthenticated, user, permissionsStatus } = useAppSelector((state) => state.auth)
  
  // Redirect ke login jika belum authenticated
  // Ini sebagai safety net, meskipun children sudah di-protect dengan PrivateRoute
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  // Ref untuk mencegah multiple refresh bersamaan
  const lastRefreshedUserIdRef = useRef<number | null>(null)
  const hasRefreshedRef = useRef(false)

  // Auto-refresh permissions HANYA SEKALI saat mount atau saat user.id berubah
  // OPTIMASI: Jangan refresh lagi jika sudah succeeded untuk mencegah redundant calls
  useEffect(() => {
    let isMounted = true

    // Skip jika:
    // - belum login atau tidak ada user
    // - sedang loading (prevent concurrent calls)
    // - sudah succeeded (tidak perlu refresh lagi)
    // - sudah failed (prevent infinite retry - hanya retry manual)
    if (
      !isAuthenticated ||
      !user ||
      !user.id ||
      permissionsStatus === 'loading' ||
      permissionsStatus === 'succeeded' ||
      (permissionsStatus === 'failed' && hasRefreshedRef.current)
    ) {
      return
    }

    // Hanya refresh jika:
    // - user.id berbeda dari yang terakhir di-refresh (user baru login atau switch user)
    // - ATAU belum pernah refresh sama sekali (initial mount)
    // - ATAU status idle (baru login, belum pernah refresh)
    const shouldRefresh = 
      lastRefreshedUserIdRef.current !== user.id ||
      (!hasRefreshedRef.current && permissionsStatus === 'idle')

    if (shouldRefresh) {
      lastRefreshedUserIdRef.current = user.id
      hasRefreshedRef.current = true

      dispatch(refreshUserPermissions())
        .then(() => {
          if (isMounted) {
            // Success - tidak perlu reset, biarkan tetap succeeded
          }
        })
        .catch((error) => {
          if (isMounted) {
            console.warn('Auto-refresh permissions gagal:', error)
            // Reset hanya jika network error dan setelah timeout
            const errorCode = error?.code || error?.message || ''
            if (
              errorCode.includes('ERR_NETWORK') ||
              errorCode.includes('ERR_INSUFFICIENT_RESOURCES') ||
              errorCode.includes('Network Error')
            ) {
              // Reset setelah 30 detik untuk allow manual retry
              setTimeout(() => {
                if (isMounted) {
                  lastRefreshedUserIdRef.current = null
                  hasRefreshedRef.current = false
                }
              }, 30000)
            }
          }
        })
    }

    return () => {
      isMounted = false
    }
    // OPTIMASI: Hanya trigger saat user.id berubah, tidak trigger saat permissionsStatus berubah
    // untuk mencegah redundant refresh calls
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.id])

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

