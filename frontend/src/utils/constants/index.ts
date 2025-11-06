export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  INVENTORY: '/inventory',
  INVENTORY_STOCK_IN: '/inventory/stock-in',
  INVENTORY_MATERIALS: '/inventory/materials',
  INVENTORY_MANDORS: '/inventory/mandors',
  INVENTORY_STOCK_OUT: '/inventory/stock-out',
  INVENTORY_RETURNS: '/inventory/returns',
  INVENTORY_INSTALLED: '/inventory/installed',
  INVENTORY_SURAT_PERMINTAAN: '/inventory/surat-permintaan',
  USER_MANAGEMENT: '/user-management',
  USER_MANAGEMENT_USERS: '/user-management/users',
  USER_MANAGEMENT_ROLES: '/user-management/roles',
  USER_MANAGEMENT_PERMISSIONS: '/user-management/permissions',
} as const
