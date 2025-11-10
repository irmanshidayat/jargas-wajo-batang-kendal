export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    PROFILE: '/auth/profile',
  },
  // Dashboard
  DASHBOARD: {
    STATS: '/dashboard/stats',
  },
  // Users
  USERS: {
    GET_ALL: '/users',
    GET_BY_ID: (id: number) => `/users/${id}`,
    CREATE: '/users',
    UPDATE: (id: number) => `/users/${id}`,
    PATCH: (id: number) => `/users/${id}`,
    DELETE: (id: number) => `/users/${id}`,
    UPDATE_PASSWORD: (id: number) => `/users/${id}/password`,
  },
  // Roles
  ROLES: {
    GET_ALL: '/roles',
    GET_BY_ID: (id: number) => `/roles/${id}`,
    CREATE: '/roles',
    UPDATE: (id: number) => `/roles/${id}`,
    PATCH: (id: number) => `/roles/${id}`,
    DELETE: (id: number) => `/roles/${id}`,
    ASSIGN_PERMISSIONS: (id: number) => `/roles/${id}/permissions`,
    ASSIGN_PERMISSIONS_CRUD: (id: number) => `/roles/${id}/permissions-crud`,
  },
  // Permissions
  PERMISSIONS: {
    GET_ALL: '/permissions',
    GET_BY_ID: (id: number) => `/permissions/${id}`,
    CREATE: '/permissions',
    UPDATE: (id: number) => `/permissions/${id}`,
    DELETE: (id: number) => `/permissions/${id}`,
    GET_USER_PERMISSIONS: (userId: number) => `/permissions/user/${userId}`,
    ASSIGN_USER_PERMISSIONS: (userId: number) => `/permissions/user/${userId}`,
    PAGES: {
      GET_ALL: '/permissions/pages',
      GET_BY_ID: (id: number) => `/permissions/pages/${id}`,
      CREATE: '/permissions/pages',
      UPDATE: (id: number) => `/permissions/pages/${id}`,
      DELETE: (id: number) => `/permissions/pages/${id}`,
    },
    USER_MENU_PREFERENCES: {
      GET_ALL: (userId: number) => `/permissions/user/${userId}/menu-preferences`,
      GET_BY_PAGE: (userId: number, pageId: number) => `/permissions/user/${userId}/menu-preferences/${pageId}`,
      CREATE_OR_UPDATE: (userId: number) => `/permissions/user/${userId}/menu-preferences`,
      BULK_UPDATE: (userId: number) => `/permissions/user/${userId}/menu-preferences/bulk`,
      DELETE: (userId: number, pageId: number) => `/permissions/user/${userId}/menu-preferences/${pageId}`,
    },
  },
  // Projects
  PROJECTS: {
    GET_ALL: '/projects/projects',
    MY_PROJECTS: '/auth/projects',
    GET_BY_ID: (id: number) => `/projects/projects/${id}`,
    CREATE: '/projects/projects',
    UPDATE: (id: number) => `/projects/projects/${id}`,
    DELETE: (id: number) => `/projects/projects/${id}`,
  },
  // Inventory - Materials
  INVENTORY: {
    MATERIALS: {
      GET_ALL: '/inventory/materials',
      GET_BY_ID: (id: number) => `/inventory/materials/${id}`,
      CREATE: '/inventory/materials',
      UPDATE: (id: number) => `/inventory/materials/${id}`,
      BULK_IMPORT: '/inventory/materials/bulk-import',
      TEMPLATE: '/inventory/materials-template',
      UNIQUE_SATUANS: '/inventory/materials/unique/satuans',
      UNIQUE_KATEGORIS: '/inventory/materials/unique/kategoris',
    },
    // Inventory - Mandors
    MANDORS: {
      GET_ALL: '/inventory/mandors',
      GET_BY_ID: (id: number) => `/inventory/mandors/${id}`,
      CREATE: '/inventory/mandors',
      UPDATE: (id: number) => `/inventory/mandors/${id}`,
    },
    // Inventory - Stock In
    STOCK_IN: {
      GET_ALL: '/inventory/stock-in',
      GET_BY_ID: (id: number) => `/inventory/stock-in/${id}`,
      CREATE: '/inventory/stock-in',
      CREATE_BULK: '/inventory/stock-in/bulk',
      UPDATE: (id: number) => `/inventory/stock-in/${id}`,
    },
    // Inventory - Stock Out
    STOCK_OUT: {
      GET_ALL: '/inventory/stock-out',
      GET_BY_ID: (id: number) => `/inventory/stock-out/${id}`,
      GET_BY_MANDOR: (mandorId: number) => `/inventory/stock-out/by-mandor/${mandorId}`,
      GET_BY_NOMOR: (nomor: string) => `/inventory/stock-out/by-nomor/${nomor}`,
      CREATE: '/inventory/stock-out',
      CREATE_BULK: '/inventory/stock-out/bulk',
    },
    // Inventory - Installed
    INSTALLED: {
      GET_ALL: '/inventory/installed',
      GET_BY_ID: (id: number) => `/inventory/installed/${id}`,
      CREATE: '/inventory/installed',
    },
    // Inventory - Returns
    RETURNS: {
      GET_ALL: '/inventory/returns',
      GET_BY_ID: (id: number) => `/inventory/returns/${id}`,
      CREATE: '/inventory/returns',
      RELEASE: (id: number) => `/inventory/returns/${id}/stock-out`,
    },
    // Inventory - Stock Balance
    STOCK_BALANCE: {
      GET_ALL: '/inventory/stock-balance',
    },
    // Inventory - Discrepancy
    DISCREPANCY: {
      CHECK: '/inventory/discrepancy',
    },
    // Inventory - Notifications
    NOTIFICATIONS: {
      GET_ALL: '/inventory/notifications',
      MARK_READ: (id: number) => `/inventory/notifications/${id}/read`,
    },
    // Inventory - Surat Permintaan
    SURAT_PERMINTAAN: {
      GET_ALL: '/inventory/surat-permintaan',
      GET_BY_ID: (id: number) => `/inventory/surat-permintaan/${id}`,
      GET_BY_NOMOR: (nomor_surat: string) => `/inventory/surat-permintaan/by-nomor/${nomor_surat}`,
      CREATE: '/inventory/surat-permintaan',
    },
    // Inventory - Surat Jalan
    SURAT_JALAN: {
      GET_ALL: '/inventory/surat-jalan',
      GET_BY_ID: (id: number) => `/inventory/surat-jalan/${id}`,
      CREATE: '/inventory/surat-jalan',
      UPDATE: (id: number) => `/inventory/surat-jalan/${id}`,
      DELETE: (id: number) => `/inventory/surat-jalan/${id}`,
    },
    // Inventory - Export
    EXPORT_EXCEL: '/inventory/export-excel',
  },
} as const
