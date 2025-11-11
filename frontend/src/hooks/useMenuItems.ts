import { useMemo, useRef } from 'react'
import { useAppSelector } from '@/store/hooks'
import { userManagementApi } from '@/features/user-management/services/userManagementApi'
import { useState, useEffect } from 'react'
import type { Page, UserMenuPreference } from '@/features/user-management/types'
import { ROUTES } from '@/utils/constants'
import { isSuperuser } from '@/utils/auth'

// Flag global untuk mencegah fetch preferences jika ada network error
let hasNetworkError = false
let networkErrorResetTimeout: NodeJS.Timeout | null = null

const resetNetworkErrorFlag = () => {
  if (networkErrorResetTimeout) {
    clearTimeout(networkErrorResetTimeout)
  }
  networkErrorResetTimeout = setTimeout(() => {
    hasNetworkError = false
  }, 10000) // Reset setelah 10 detik
}

interface MenuItem {
  label: string
  path: string
  icon?: string
  order: number
}

/**
 * Helper function untuk format page_name menjadi display_name yang lebih baik
 */
const formatPageName = (pageName?: string, path?: string): string => {
  if (!pageName && !path) return 'Menu'
  
  if (pageName) {
    // Convert snake_case atau kebab-case ke Title Case
    return pageName
      .replace(/_/g, ' ')
      .replace(/-/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }
  
  // Fallback: use path segment
  if (path) {
    const segments = path.split('/').filter(Boolean)
    const lastSegment = segments[segments.length - 1]
    return lastSegment
      .replace(/-/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }
  
  return 'Menu'
}

/**
 * Hook untuk mendapatkan menu items secara dinamis dari permissions user
 * Menu akan otomatis ter-update ketika permissions berubah
 */
export const useMenuItems = () => {
  const { user, permissionsStatus } = useAppSelector((state) => state.auth)
  const [allPages, setAllPages] = useState<Page[]>([])
  const [loadingPages, setLoadingPages] = useState(false)
  const [userMenuPreferences, setUserMenuPreferences] = useState<Map<number, boolean>>(new Map())
  const [loadingPreferences, setLoadingPreferences] = useState(false)
  
  // Ref untuk mencegah multiple concurrent requests
  const isFetchingPagesRef = useRef(false)
  const isFetchingPreferencesRef = useRef(false)
  const lastFetchedUserIdRef = useRef<number | null>(null)
  const hasFetchedForSucceededRef = useRef(false) // Track apakah sudah fetch saat status succeeded
  const lastPermissionsStatusRef = useRef<string>('idle') // Track status terakhir

  // Fetch semua pages untuk superuser agar bisa lihat semua menu
  useEffect(() => {
    const fetchPages = async () => {
      if (!user) return
      
      // Mencegah multiple concurrent requests
      if (isFetchingPagesRef.current) {
        return
      }
      
      // Hanya superuser yang bisa fetch pages (karena endpoint memerlukan superuser)
      if (isSuperuser(user)) {
        try {
          isFetchingPagesRef.current = true
          setLoadingPages(true)
          // Backend membatasi limit maksimal 100, jadi kita fetch dengan pagination
          // Fetch semua pages dengan multiple requests jika perlu
          let allPagesData: Page[] = []
          let currentPage = 1
          const limit = 100 // Maksimal yang diizinkan backend
          let hasMore = true
          
          while (hasMore) {
            const response = await userManagementApi.getPages(currentPage, limit)
            const pagesData = Array.isArray(response.data) ? response.data : []
            allPagesData = [...allPagesData, ...pagesData]
            
            // Check apakah masih ada halaman berikutnya
            const totalPages = Math.ceil(response.total / limit)
            hasMore = currentPage < totalPages
            currentPage++
            
            // Safety limit: max 10 pages (1000 items) untuk menghindari infinite loop
            if (currentPage > 10) break
          }
          
          setAllPages(allPagesData)
        } catch (error: any) {
          console.error('Error fetching pages for menu:', error)
          // Jika error (misal network issue), tetap set empty
          // Fallback akan menggunakan permissions
          setAllPages([])
        } finally {
          setLoadingPages(false)
          isFetchingPagesRef.current = false
        }
      } else {
        // Non-superuser tidak perlu fetch, akan menggunakan info dari permissions
        setAllPages([])
        isFetchingPagesRef.current = false
      }
    }

    fetchPages()
  }, [user?.id, user?.is_superuser]) // Re-fetch jika superuser status berubah

  // Fetch user menu preferences - HANYA SEKALI saat permissions status pertama kali menjadi succeeded
  // OPTIMASI: Hanya trigger saat permissionsStatus === 'succeeded' untuk mencegah redundant calls
  useEffect(() => {
    // Early return guards - check sebelum memanggil async function
    if (!user?.id) return
    
    // HANYA fetch jika permissions status SUCCEEDED
    // Ini penting untuk mencegah fetch saat permissions belum siap atau sedang loading
    if (permissionsStatus !== 'succeeded') {
      return
    }
    
    // Skip fetch jika ada network error sebelumnya (untuk mencegah infinite loop)
    if (hasNetworkError) {
      return
    }
    
    // Mencegah multiple concurrent requests untuk user yang sama
    if (isFetchingPreferencesRef.current && lastFetchedUserIdRef.current === user.id) {
      return
    }
    
    // Reset flag jika user.id berubah (user baru login atau switch user)
    if (lastFetchedUserIdRef.current !== user.id) {
      hasFetchedForSucceededRef.current = false
      lastPermissionsStatusRef.current = 'idle'
    }
    
    // Skip jika user id sama dengan yang sudah di-fetch DAN sudah pernah fetch untuk status succeeded
    // Hanya fetch jika user id berbeda atau belum pernah fetch untuk status succeeded
    if (lastFetchedUserIdRef.current === user.id && hasFetchedForSucceededRef.current) {
      return
    }
    
    // Skip jika user belum memiliki permissions (berarti belum siap)
    // Ini penting untuk mencegah fetch saat user baru login dan permissions belum di-load
    if (!user.permissions || !Array.isArray(user.permissions) || user.permissions.length === 0) {
      // Untuk non-admin, tunggu sampai permissions di-load
      // Untuk admin, bisa langsung fetch karena admin biasanya punya semua permissions
      if (!isSuperuser(user)) {
        return
      }
    }
    
    const fetchPreferences = async () => {
      try {
        isFetchingPreferencesRef.current = true
        lastFetchedUserIdRef.current = user.id
        hasFetchedForSucceededRef.current = true
        lastPermissionsStatusRef.current = permissionsStatus
        setLoadingPreferences(true)
        const preferences = await userManagementApi.getUserMenuPreferences(user.id)
        const preferencesMap = new Map<number, boolean>()
        preferences.forEach(pref => {
          preferencesMap.set(pref.page_id, pref.show_in_menu)
        })
        setUserMenuPreferences(preferencesMap)
        // Reset network error flag jika berhasil
        hasNetworkError = false
      } catch (error: any) {
        // Skip CanceledError - ini expected behavior saat cancel duplicate request
        // Request di-cancel karena duplicate, tidak perlu handle sebagai error
        if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
          // Request di-cancel karena duplicate, request baru yang sedang berjalan akan handle hasilnya
          // Tidak perlu reset flag atau log error
          return
        }
        
        console.error('Error fetching user menu preferences:', error)
        // Jika error, reset flag agar bisa retry
        hasFetchedForSucceededRef.current = false
        // Jika error, default ke empty map (semua menu akan ditampilkan)
        const errorCode = error?.code || error?.message || ''
        if (errorCode.includes('ERR_NETWORK') || 
            errorCode.includes('ERR_INSUFFICIENT_RESOURCES') ||
            errorCode.includes('Network Error')) {
          // Set flag global untuk mencegah fetch berulang
          hasNetworkError = true
          resetNetworkErrorFlag()
          // Reset lastFetchedUserIdRef agar bisa retry setelah timeout
          lastFetchedUserIdRef.current = null
        }
        setUserMenuPreferences(new Map())
      } finally {
        // Cleanup hanya jika bukan CanceledError (karena CanceledError sudah return di catch)
        setLoadingPreferences(false)
        isFetchingPreferencesRef.current = false
      }
    }

    fetchPreferences()
    // OPTIMASI: Hanya trigger saat user.id berubah atau permissionsStatus berubah
    // Guard di dalam effect memastikan hanya fetch saat status === 'succeeded'
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, permissionsStatus])

  // Helper untuk deduplikasi khusus kasus Installed: buang '/list' jika base ada
  const dedupeInstalledMenu = (items: MenuItem[]): MenuItem[] => {
    const hasInstalledBase = items.some(i => i.path === ROUTES.INVENTORY_INSTALLED)
    if (!hasInstalledBase) return items
    return items.filter(i => i.path !== `${ROUTES.INVENTORY_INSTALLED}/list`)
  }

  const menuItems = useMemo(() => {
    if (!user) return []

    // SUPERUSER/ADMIN: return semua pages yang ada di sistem (jika sudah di-fetch)
    // Atau gunakan permissions sebagai fallback jika pages belum ter-fetch
    if (isSuperuser(user)) {
      if (allPages.length > 0) {
        // Jika pages sudah di-fetch, gunakan itu
        // Filter berdasarkan user menu preferences
        return dedupeInstalledMenu(
          allPages
          .filter(page => page.path !== '/') // Exclude root path
          .filter(page => {
            // Jika ada preference, gunakan preference
            // Jika tidak ada preference, default ke true (tampilkan)
            const showInMenu = userMenuPreferences.get(page.id)
            return showInMenu !== false // true atau undefined = tampilkan
          })
          .map(page => ({
            label: page.display_name,
            path: page.path,
            icon: page.icon,
            order: page.order,
          }))
          .sort((a, b) => a.order - b.order)
        )
      } else {
        // Fallback: jika pages belum ter-fetch, gunakan permissions
        // Superuser biasanya punya semua permissions, jadi ini akan work
        // Atau kita bisa return empty dan let it load
        if (user.permissions && Array.isArray(user.permissions) && user.permissions.length > 0) {
          const permissionMap = new Map<string, { 
            page_id: number
            page_name?: string
            page_path: string
            display_name?: string
          }>()

          user.permissions.forEach((perm) => {
            if (perm.can_read === true && perm.page_path) {
              const path = perm.page_path.trim()
              if (!path || path === '/') return
              if (!permissionMap.has(path)) {
                permissionMap.set(path, {
                  page_id: perm.page_id,
                  page_name: perm.page_name,
                  page_path: path,
                  display_name: perm.display_name,
                })
              }
            }
          })

          const items: MenuItem[] = []
          permissionMap.forEach((permInfo) => {
            items.push({
              label: permInfo.display_name || formatPageName(permInfo.page_name, permInfo.page_path),
              path: permInfo.page_path,
              order: items.length + 100,
            })
          })

          return dedupeInstalledMenu(items).sort((a, b) => a.path.localeCompare(b.path))
        }
        // Jika belum ada permissions juga, return empty (akan di-update setelah pages di-fetch)
        return []
      }
    }

    // Non-superuser: ambil menu dari permissions yang punya can_read = true
    if (!user.permissions || !Array.isArray(user.permissions) || user.permissions.length === 0) {
      return []
    }

    // Get unique page paths dari permissions yang memiliki can_read = true
    const permissionMap = new Map<string, { 
      page_id: number
      page_name?: string
      page_path: string
      display_name?: string
    }>()

    user.permissions.forEach((perm) => {
      if (perm.can_read === true && perm.page_path) {
        const path = perm.page_path.trim()
        // Skip jika path kosong atau root path
        if (!path || path === '/') return
        
        // Store permission info (jika ada duplicate, keep first one)
        if (!permissionMap.has(path)) {
          permissionMap.set(path, {
            page_id: perm.page_id,
            page_name: perm.page_name,
            page_path: path,
            display_name: perm.display_name,
          })
        }
      }
    })

    // Buat menu items dari permissions
    // Untuk non-superuser, kita gunakan info dari permission
    // dan jika superuser sudah fetch pages, kita bisa enrich dengan info dari pages
    const items: MenuItem[] = []
    
    permissionMap.forEach((permInfo) => {
      // Coba cari page info dari allPages jika ada (untuk superuser)
      const pageInfo = allPages.find(p => p.path === permInfo.page_path)
      
      // Filter berdasarkan user menu preferences
      // Jika ada pageInfo dan ada preference, gunakan preference
      // Jika tidak ada preference, default ke true (tampilkan)
      if (pageInfo) {
        const showInMenu = userMenuPreferences.get(pageInfo.id)
        if (showInMenu === false) {
          return // Skip menu ini
        }
      }
      
      // Prioritas: display_name dari permission > display_name dari pageInfo > formatPageName
      const label = permInfo.display_name || pageInfo?.display_name || formatPageName(permInfo.page_name, permInfo.page_path)
      
      items.push({
        label: label,
        path: permInfo.page_path,
        icon: pageInfo?.icon,
        // Gunakan order dari page jika ada, jika tidak gunakan order berdasarkan path
        order: pageInfo?.order ?? (items.length + 100), // Default order tinggi
      })
    })

    // Dedup khusus installed, lalu sort berdasarkan order atau path
    const finalItems = dedupeInstalledMenu(items)
    return finalItems.sort((a, b) => {
      // Jika ada order yang sama, sort berdasarkan path
      if (a.order === b.order) {
        return a.path.localeCompare(b.path)
      }
      return a.order - b.order
    })
  }, [user, allPages, loadingPages, userMenuPreferences])

  return { menuItems, loading: loadingPages || loadingPreferences }
}

