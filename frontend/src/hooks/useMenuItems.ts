import { useMemo } from 'react'
import { useAppSelector } from '@/store/hooks'
import { userManagementApi } from '@/features/user-management/services/userManagementApi'
import { useState, useEffect } from 'react'
import type { Page, UserMenuPreference } from '@/features/user-management/types'
import { ROUTES } from '@/utils/constants'

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
  const { user } = useAppSelector((state) => state.auth)
  const [allPages, setAllPages] = useState<Page[]>([])
  const [loadingPages, setLoadingPages] = useState(false)
  const [userMenuPreferences, setUserMenuPreferences] = useState<Map<number, boolean>>(new Map())
  const [loadingPreferences, setLoadingPreferences] = useState(false)

  // Fetch semua pages untuk superuser agar bisa lihat semua menu
  useEffect(() => {
    const fetchPages = async () => {
      if (!user) return
      
      const isSuperuser = user.is_superuser === true || 
                          user.is_superuser === 1 || 
                          user.is_superuser === '1' ||
                          String(user.is_superuser).toLowerCase() === 'true'
      
      // Hanya superuser yang bisa fetch pages (karena endpoint memerlukan superuser)
      if (isSuperuser) {
        try {
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
        }
      } else {
        // Non-superuser tidak perlu fetch, akan menggunakan info dari permissions
        setAllPages([])
      }
    }

    fetchPages()
  }, [user?.id, user?.is_superuser]) // Re-fetch jika superuser status berubah

  // Fetch user menu preferences
  useEffect(() => {
    const fetchPreferences = async () => {
      if (!user?.id) return
      
      try {
        setLoadingPreferences(true)
        const preferences = await userManagementApi.getUserMenuPreferences(user.id)
        const preferencesMap = new Map<number, boolean>()
        preferences.forEach(pref => {
          preferencesMap.set(pref.page_id, pref.show_in_menu)
        })
        setUserMenuPreferences(preferencesMap)
      } catch (error: any) {
        console.error('Error fetching user menu preferences:', error)
        // Jika error, default ke empty map (semua menu akan ditampilkan)
        setUserMenuPreferences(new Map())
      } finally {
        setLoadingPreferences(false)
      }
    }

    fetchPreferences()
  }, [user?.id])

  // Helper untuk deduplikasi khusus kasus Installed: buang '/list' jika base ada
  const dedupeInstalledMenu = (items: MenuItem[]): MenuItem[] => {
    const hasInstalledBase = items.some(i => i.path === ROUTES.INVENTORY_INSTALLED)
    if (!hasInstalledBase) return items
    return items.filter(i => i.path !== `${ROUTES.INVENTORY_INSTALLED}/list`)
  }

  const menuItems = useMemo(() => {
    if (!user) return []

    const isSuperuser = user.is_superuser === true || 
                        user.is_superuser === 1 || 
                        user.is_superuser === '1' ||
                        String(user.is_superuser).toLowerCase() === 'true'

    // SUPERUSER/ADMIN: return semua pages yang ada di sistem (jika sudah di-fetch)
    // Atau gunakan permissions sebagai fallback jika pages belum ter-fetch
    if (isSuperuser) {
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
                })
              }
            }
          })

          const items: MenuItem[] = []
          permissionMap.forEach((permInfo) => {
            items.push({
              label: formatPageName(permInfo.page_name, permInfo.page_path),
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
      
      items.push({
        label: pageInfo?.display_name || formatPageName(permInfo.page_name, permInfo.page_path),
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

