import React, { useMemo } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ROUTES } from '@/utils/constants'
import { useAppSelector } from '@/store/hooks'
import { useMenuItems } from '@/hooks/useMenuItems'

interface MenuItem {
  label: string
  path: string
  icon?: string
  order: number
}

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation()
  const { user } = useAppSelector((state) => state.auth)
  const { menuItems: allMenuItemsFromPermissions } = useMenuItems()

  // Filter menu items - Dashboard selalu muncul untuk semua user yang sudah login
  // Menu lainnya akan muncul berdasarkan permissions dari role
  const visibleMenuItems = useMemo(() => {
    if (!user) {
      return []
    }

    // Dashboard selalu bisa diakses (sudah di-handle di PrivateRoute sebagai exception)
    const dashboardItem: MenuItem = {
      label: 'Dashboard',
      path: ROUTES.DASHBOARD,
      order: 0, // Urutan pertama
    }

    // Filter out Dashboard dari allMenuItemsFromPermissions untuk menghindari duplikasi
    const filteredMenuItems = allMenuItemsFromPermissions.filter(
      (item) => item.path !== ROUTES.DASHBOARD
    )

    // Gabungkan dashboard dengan menu items dari permissions (tanpa duplikasi)
    const items = [dashboardItem, ...filteredMenuItems]
    
    // Sort berdasarkan order
    return items.sort((a, b) => a.order - b.order)
  }, [user, allMenuItemsFromPermissions])

  // Group menu items secara dinamis berdasarkan path prefix
  // Tidak ada hardcode grouping, semua berdasarkan permissions
  const groupedMenuItems = useMemo(() => {
    const groups = new Map<string, MenuItem[]>()
    
    visibleMenuItems.forEach((item) => {
      // Skip dashboard dari grouping
      if (item.path === ROUTES.DASHBOARD) {
        if (!groups.has('main')) {
          groups.set('main', [])
        }
        groups.get('main')!.push(item)
        return
      }

      // Tentukan group berdasarkan path prefix
      // Contoh: /inventory/* -> group "inventory", /user-management/* -> group "main"
      let groupName = 'main'
      const pathSegments = item.path.split('/').filter(Boolean)
      
      if (pathSegments.length > 0) {
        const firstSegment = pathSegments[0]
        
        // Jika path punya lebih dari 1 segment, masukkan ke group berdasarkan segment pertama
        if (pathSegments.length > 1) {
          groupName = firstSegment
        } else {
          // Single segment path -> main menu
          groupName = 'main'
        }
      }

      if (!groups.has(groupName)) {
        groups.set(groupName, [])
      }
      groups.get(groupName)!.push(item)
    })

    return groups
  }, [visibleMenuItems])

  return (
    <>
      {/* Overlay for mobile/tablet */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`bg-gradient-to-b from-indigo-50 via-purple-50 to-white text-slate-800 w-64 h-screen fixed left-0 top-0 shadow-xl border-r border-indigo-100 z-50 transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:flex`}
      >
        {/* Header - Fixed */}
        <div className="flex items-center justify-between p-4 sm:p-6 pb-4 flex-shrink-0">
          <h2 className="text-lg sm:text-xl font-bold text-slate-900">Jargas APBN</h2>
          {/* Close button for mobile/tablet */}
          <button
            onClick={onClose}
            className="lg:hidden p-2 rounded-lg hover:bg-slate-200 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500"
            aria-label="Close menu"
          >
            <svg
              className="w-5 h-5 text-slate-700"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        {/* Navigation - Scrollable untuk semua ukuran layar (desktop, tablet, mobile) */}
        <nav 
          className="flex-1 overflow-y-auto overflow-x-hidden px-4 sm:px-6 pb-4 sm:pb-6 overscroll-contain"
          style={{ 
            WebkitOverflowScrolling: 'touch',
            maxHeight: 'calc(100vh - 96px)'
          }}
        >
          <ul className="space-y-1">
            {Array.from(groupedMenuItems.entries()).map(([groupName, items]) => {
              // Main group tidak perlu header
              const isMainGroup = groupName === 'main'
              
              return (
                <React.Fragment key={groupName}>
                  {!isMainGroup && (
                    <li className="pt-4 mt-4 border-t border-indigo-200">
                      <div className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        {groupName.charAt(0).toUpperCase() + groupName.slice(1)}
                      </div>
                    </li>
                  )}
                  {items.map((item) => {
                    const isActive = location.pathname === item.path
                    return (
                      <li key={item.path}>
                        <Link
                          to={item.path}
                          onClick={onClose}
                          className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium ${
                            isActive
                              ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg scale-[1.02]'
                              : 'text-slate-700 hover:bg-indigo-50 hover:text-slate-900'
                          }`}
                        >
                          {item.label}
                        </Link>
                      </li>
                    )
                  })}
                </React.Fragment>
              )
            })}
          </ul>
        </nav>
      </aside>
    </>
  )
}

export default Sidebar
