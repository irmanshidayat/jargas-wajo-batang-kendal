import { Navigate, useLocation } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'

interface PrivateRouteProps {
  children: React.ReactNode
  requiredPermission?: 'read' | 'write'
}

const PrivateRoute = ({ children, requiredPermission }: PrivateRouteProps) => {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth)
  const { currentProject } = useAppSelector((state) => state.project)
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Check project selection - kecuali untuk halaman select-project sendiri
  // Jika belum pilih project dan bukan di halaman select-project, redirect ke select-project
  if (!currentProject && location.pathname !== '/select-project') {
    return <Navigate to="/select-project" replace />
  }

  // Jika sudah di select-project dan sudah punya project, redirect ke dashboard
  if (currentProject && location.pathname === '/select-project') {
    return <Navigate to="/dashboard" replace />
  }

  // Check apakah user adalah superuser/admin
  const isSuperuser = user?.is_superuser === true || 
                      user?.is_superuser === 1 || 
                      user?.is_superuser === '1' ||
                      String(user?.is_superuser).toLowerCase() === 'true'
  
  // SUPERUSER/ADMIN: Selalu punya akses ke SEMUA halaman tanpa terkecuali
  // Bypass semua permission check untuk superuser
  if (isSuperuser) {
    return <>{children}</>
  }

  // Exception: Dashboard bisa diakses semua user yang sudah login
  // Ini adalah halaman default yang aman untuk semua user
  if (location.pathname === '/dashboard' || location.pathname === '/') {
    return <>{children}</>
  }

  // Untuk non-superuser, selalu check permissions (baik dengan atau tanpa requiredPermission)
  // Jika tidak punya permissions sama sekali, DENY access
  if (!user || !user.permissions || !Array.isArray(user.permissions) || user.permissions.length === 0) {
    return <Navigate to="/dashboard" replace />
  }

  // Determine permission requirement (default to 'read' jika tidak specified)
  const permissionNeeded = requiredPermission || 'read'

  // Check permission berdasarkan path dengan STRICT matching
  // Hanya exact match yang diizinkan - tidak ada parent-child inheritance
  const hasPermission = user.permissions.some((perm) => {
    // Check CRUD permission sesuai permissionNeeded
    let canAccess = false
    if (permissionNeeded === 'read') {
      canAccess = perm.can_read === true
    } else {
      // write permission berarti minimal ada salah satu CRUD yang true
      canAccess = perm.can_read || perm.can_create || perm.can_update || perm.can_delete
    }
    
    if (!canAccess) {
      return false
    }
    
    // Normalize paths untuk comparison
    const permPath = (perm.page_path || '').trim()
    const currentPath = location.pathname.trim()
    
    // STRICT CHECK: Hanya exact match yang diizinkan
    // Tidak ada parent-child inheritance untuk security
    if (permPath === currentPath) {
      return true
    }
    
    return false
  })
  
  if (!hasPermission) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

export default PrivateRoute
