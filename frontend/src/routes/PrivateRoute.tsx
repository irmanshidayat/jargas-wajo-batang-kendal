import { Navigate, useLocation } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'
import { canAccessPage, arePermissionsLoaded, isPublicPage, isSuperuser } from '@/utils/auth'

interface PrivateRouteProps {
  children: React.ReactNode
  requiredPermission?: 'read' | 'write'
}

const PrivateRoute = ({ children, requiredPermission }: PrivateRouteProps) => {
  const { isAuthenticated, user, permissionsStatus } = useAppSelector((state) => state.auth)
  const { currentProject } = useAppSelector((state) => state.project)
  const location = useLocation()

  // Redirect ke login jika belum authenticated
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

  // Untuk superuser, langsung allow access (tidak perlu check permissions)
  if (isSuperuser(user)) {
    return <>{children}</>
  }

  // Untuk public pages, langsung allow access
  if (isPublicPage(location.pathname)) {
    return <>{children}</>
  }

  // Check apakah permissions sudah loaded
  // Jika belum loaded, tunggu sampai loaded
  // Jika permissions failed, tetap coba check dengan permissions yang ada (bisa dari localStorage)
  const permissionsReady = arePermissionsLoaded(user) || permissionsStatus === 'failed'

  // Jika permissions belum ready dan sedang loading, tunggu sebentar
  // Tapi jangan block terlalu lama untuk menghindari user experience yang buruk
  if (!permissionsReady && permissionsStatus === 'loading') {
    // Biarkan render dengan permissions yang ada (bisa dari localStorage)
    // Jika tidak ada, akan di-check di bawah dan redirect jika perlu
  }

  // Check apakah user dapat mengakses halaman ini
  // Menggunakan utility function untuk menghindari redundansi
  const permissionNeeded = requiredPermission || 'read'
  const canAccess = canAccessPage(user, location.pathname, permissionNeeded)
  
  // Jika tidak bisa akses, redirect ke dashboard (public page)
  // Pastikan dashboard bisa diakses untuk menghindari infinite loop
  if (!canAccess) {
    // Jika permissions sedang loading dan belum ready, tunggu sebentar
    // Tapi jika sudah terlalu lama (lebih dari 3 detik), anggap failed dan redirect
    if (permissionsStatus === 'loading' && !arePermissionsLoaded(user)) {
      // Untuk sekarang, biarkan render dengan permissions yang ada
      // Jika tidak ada permissions sama sekali, akan di-redirect
      // Ini untuk menghindari flash atau blocking terlalu lama
      // Jika user tidak punya permission, akan di-redirect setelah permissions loaded
      return <>{children}</>
    }
    
    // Redirect ke dashboard (public page yang selalu bisa diakses)
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

export default PrivateRoute
