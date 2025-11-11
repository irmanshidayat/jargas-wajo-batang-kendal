/**
 * Utility functions untuk authentication dan authorization
 * Centralized logic untuk menghindari redundansi
 */

interface User {
  id: number
  email: string
  name: string
  is_active: boolean
  is_superuser?: boolean | number | string
  permissions?: Array<{
    id: number
    page_id: number
    page_name?: string
    page_path?: string
    display_name?: string
    can_create: boolean
    can_read: boolean
    can_update: boolean
    can_delete: boolean
  }>
}

/**
 * Whitelist halaman yang tidak perlu permission check
 * Halaman-halaman ini bisa diakses oleh semua user yang sudah login
 */
const PUBLIC_PAGES = [
  '/dashboard',
  '/',
  '/select-project',
]

/**
 * Normalize path untuk comparison (remove trailing slash)
 * @param path - Path yang akan di-normalize
 * @returns Path yang sudah di-normalize
 */
const normalizePath = (path: string): string => {
  // Remove trailing slash dan trim, tapi tetap preserve case
  // karena path di URL biasanya case-sensitive
  return path.trim().replace(/\/$/, '')
}

/**
 * Check apakah path adalah public page (tidak perlu permission)
 * @param path - Path halaman yang ingin diakses
 * @returns true jika path adalah public page
 */
export const isPublicPage = (path: string): boolean => {
  const normalizedPath = normalizePath(path)
  return PUBLIC_PAGES.some(publicPath => normalizePath(publicPath) === normalizedPath)
}

/**
 * Check apakah user adalah superuser/admin
 * @param user - User object atau null
 * @returns true jika user adalah superuser
 */
export const isSuperuser = (user: User | null): boolean => {
  if (!user || !user.is_superuser) {
    return false
  }
  
  return (
    user.is_superuser === true ||
    user.is_superuser === 1 ||
    user.is_superuser === '1' ||
    String(user.is_superuser).toLowerCase() === 'true'
  )
}

/**
 * Check apakah permissions sudah loaded (ada di user object)
 * @param user - User object atau null
 * @returns true jika permissions sudah loaded
 */
export const arePermissionsLoaded = (user: User | null): boolean => {
  if (!user) {
    return false
  }
  
  // Permissions dianggap loaded jika:
  // 1. User adalah superuser (tidak perlu permissions)
  // 2. ATAU user.permissions adalah array (bisa kosong, tapi sudah loaded)
  if (isSuperuser(user)) {
    return true
  }
  
  return Array.isArray(user.permissions)
}

/**
 * Check apakah user memiliki permission untuk path tertentu
 * @param user - User object atau null
 * @param path - Path halaman yang ingin diakses
 * @param requiredPermission - Permission yang dibutuhkan ('read' atau 'write')
 * @returns true jika user memiliki permission
 */
export const hasPermission = (
  user: User | null,
  path: string,
  requiredPermission: 'read' | 'write' = 'read'
): boolean => {
  if (!user || !user.permissions || !Array.isArray(user.permissions) || user.permissions.length === 0) {
    return false
  }

  const normalizedPath = normalizePath(path)
  
  return user.permissions.some((perm) => {
    // Check CRUD permission sesuai requiredPermission
    let canAccess = false
    if (requiredPermission === 'read') {
      canAccess = perm.can_read === true
    } else {
      // write permission berarti minimal ada salah satu CRUD yang true
      canAccess = perm.can_read || perm.can_create || perm.can_update || perm.can_delete
    }
    
    if (!canAccess) {
      return false
    }
    
    // Normalize paths untuk comparison
    const permPath = normalizePath(perm.page_path || '')
    
    // STRICT CHECK: Hanya exact match yang diizinkan
    // Tidak ada parent-child inheritance untuk security
    return permPath === normalizedPath
  })
}

/**
 * Check apakah user dapat mengakses halaman tertentu
 * Superuser selalu punya akses, non-superuser perlu check permissions
 * @param user - User object atau null
 * @param path - Path halaman yang ingin diakses
 * @param requiredPermission - Permission yang dibutuhkan ('read' atau 'write')
 * @returns true jika user dapat mengakses halaman
 */
export const canAccessPage = (
  user: User | null,
  path: string,
  requiredPermission: 'read' | 'write' = 'read'
): boolean => {
  // Superuser selalu punya akses
  if (isSuperuser(user)) {
    return true
  }
  
  // Public pages bisa diakses semua user yang sudah login
  if (isPublicPage(path)) {
    return true
  }
  
  // Check permissions untuk non-superuser
  return hasPermission(user, path, requiredPermission)
}

