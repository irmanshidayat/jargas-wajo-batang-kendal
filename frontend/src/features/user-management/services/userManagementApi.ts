import { apiClient, API_ENDPOINTS } from '@/services/api'
import { buildPaginationQuery, buildQueryParams, extractData, extractPaginatedResponse } from '@/utils/api'
import type {
  Role,
  RoleDetail,
  Page,
  Permission,
  PermissionDetail,
  RoleCreateRequest,
  RoleUpdateRequest,
  PageCreateRequest,
  PageUpdateRequest,
  PermissionCreateRequest,
  PermissionUpdateRequest,
  AssignPermissionsRequest,
  AssignRolePermissionsCRUDRequest,
  User,
  UserCreateRequest,
  UserUpdateRequest,
  UserMenuPreference,
  UserMenuPreferenceCreateRequest,
  UserMenuPreferenceBulkRequest,
  PaginatedResponse,
} from '../types'

// In-flight memoization untuk mencegah duplicate requests menunggu promise yang sama
const inFlightMenuPrefs = new Map<number, Promise<UserMenuPreference[]>>()

export const userManagementApi = {
  // Roles
  getRoles: async (page: number = 1, limit: number = 100): Promise<PaginatedResponse<Role>> => {
    const query = buildPaginationQuery(page, limit)
    const response = await apiClient.get(`${API_ENDPOINTS.ROLES.GET_ALL}${query}`)
    return extractPaginatedResponse<Role>(response)
  },

  getRole: async (roleId: number, includePermissions: boolean = false): Promise<Role | RoleDetail> => {
    const query = buildQueryParams({ include_permissions: includePermissions })
    const response = await apiClient.get(`${API_ENDPOINTS.ROLES.GET_BY_ID(roleId)}${query}`)
    return extractData<Role | RoleDetail>(response)
  },

  createRole: async (data: RoleCreateRequest): Promise<Role> => {
    const response = await apiClient.post(API_ENDPOINTS.ROLES.CREATE, data)
    return extractData<Role>(response)
  },

  updateRole: async (roleId: number, data: RoleUpdateRequest): Promise<Role> => {
    const response = await apiClient.put(API_ENDPOINTS.ROLES.UPDATE(roleId), data)
    return extractData<Role>(response)
  },

  patchRole: async (roleId: number, data: RoleUpdateRequest): Promise<Role> => {
    const response = await apiClient.patch(API_ENDPOINTS.ROLES.PATCH(roleId), data)
    return extractData<Role>(response)
  },

  deleteRole: async (roleId: number): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.ROLES.DELETE(roleId))
  },

  assignRolePermissions: async (roleId: number, data: AssignPermissionsRequest): Promise<RoleDetail> => {
    const response = await apiClient.post(API_ENDPOINTS.ROLES.ASSIGN_PERMISSIONS(roleId), data)
    return extractData<RoleDetail>(response)
  },

  assignRolePermissionsCRUD: async (roleId: number, data: AssignRolePermissionsCRUDRequest): Promise<RoleDetail> => {
    const response = await apiClient.put(API_ENDPOINTS.ROLES.ASSIGN_PERMISSIONS_CRUD(roleId), data)
    return extractData<RoleDetail>(response)
  },

  // Pages
  getPages: async (page: number = 1, limit: number = 100): Promise<PaginatedResponse<Page>> => {
    const query = buildPaginationQuery(page, limit)
    const response = await apiClient.get(`${API_ENDPOINTS.PERMISSIONS.PAGES.GET_ALL}${query}`)
    return extractPaginatedResponse<Page>(response)
  },

  getPage: async (pageId: number): Promise<Page> => {
    const response = await apiClient.get(API_ENDPOINTS.PERMISSIONS.PAGES.GET_BY_ID(pageId))
    return extractData<Page>(response)
  },

  createPage: async (data: PageCreateRequest): Promise<Page> => {
    const response = await apiClient.post(API_ENDPOINTS.PERMISSIONS.PAGES.CREATE, data)
    return extractData<Page>(response)
  },

  updatePage: async (pageId: number, data: PageUpdateRequest): Promise<Page> => {
    const response = await apiClient.put(API_ENDPOINTS.PERMISSIONS.PAGES.UPDATE(pageId), data)
    return extractData<Page>(response)
  },

  deletePage: async (pageId: number): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.PERMISSIONS.PAGES.DELETE(pageId))
  },

  // Permissions
  getPermissions: async (page: number = 1, limit: number = 100, pageId?: number): Promise<PaginatedResponse<Permission> | Permission[]> => {
    const query = buildPaginationQuery(page, limit, { page_id: pageId })
    const response = await apiClient.get(`${API_ENDPOINTS.PERMISSIONS.GET_ALL}${query}`)
    return extractData<PaginatedResponse<Permission> | Permission[]>(response)
  },

  getPermission: async (permissionId: number): Promise<PermissionDetail> => {
    const response = await apiClient.get(API_ENDPOINTS.PERMISSIONS.GET_BY_ID(permissionId))
    return extractData<PermissionDetail>(response)
  },

  createPermission: async (data: PermissionCreateRequest): Promise<PermissionDetail> => {
    const response = await apiClient.post(API_ENDPOINTS.PERMISSIONS.CREATE, data)
    return extractData<PermissionDetail>(response)
  },

  updatePermission: async (permissionId: number, data: PermissionUpdateRequest): Promise<PermissionDetail> => {
    const response = await apiClient.put(API_ENDPOINTS.PERMISSIONS.UPDATE(permissionId), data)
    return extractData<PermissionDetail>(response)
  },

  deletePermission: async (permissionId: number): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.PERMISSIONS.DELETE(permissionId))
  },

  getUserPermissions: async (userId: number): Promise<Permission[]> => {
    const response = await apiClient.get(API_ENDPOINTS.PERMISSIONS.GET_USER_PERMISSIONS(userId))
    return extractData<Permission[]>(response)
  },

  assignUserPermissions: async (userId: number, data: AssignPermissionsRequest): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.PERMISSIONS.ASSIGN_USER_PERMISSIONS(userId), data)
  },

  // Users (from existing users API, but we'll add role management)
  getUsers: async (page: number = 1, limit: number = 100): Promise<PaginatedResponse<User>> => {
    const query = buildPaginationQuery(page, limit)
    const response = await apiClient.get(`${API_ENDPOINTS.USERS.GET_ALL}${query}`)
    return extractPaginatedResponse<User>(response)
  },

  getUser: async (userId: number): Promise<User> => {
    const response = await apiClient.get(API_ENDPOINTS.USERS.GET_BY_ID(userId))
    return extractData<User>(response)
  },

  createUser: async (data: UserCreateRequest): Promise<User> => {
    const response = await apiClient.post(API_ENDPOINTS.USERS.CREATE, data)
    return extractData<User>(response)
  },

  updateUser: async (userId: number, data: UserUpdateRequest): Promise<User> => {
    const response = await apiClient.put(API_ENDPOINTS.USERS.UPDATE(userId), data)
    return extractData<User>(response)
  },

  patchUser: async (userId: number, data: UserUpdateRequest): Promise<User> => {
    const response = await apiClient.patch(API_ENDPOINTS.USERS.PATCH(userId), data)
    return extractData<User>(response)
  },

  deleteUser: async (userId: number): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.USERS.DELETE(userId))
  },

  // User Menu Preferences
  getUserMenuPreferences: async (userId: number): Promise<UserMenuPreference[]> => {
    // Jika sudah ada request in-flight untuk userId ini, kembalikan promise yang sama
    const existing = inFlightMenuPrefs.get(userId)
    if (existing) {
      return existing
    }

    const requestPromise = (async () => {
      try {
        const response = await apiClient.get(
          API_ENDPOINTS.PERMISSIONS.USER_MENU_PREFERENCES.GET_ALL(userId)
        )
        return extractData<UserMenuPreference[]>(response)
      } finally {
        // Hapus dari map setelah selesai agar request berikutnya bisa dibuat lagi bila perlu
        inFlightMenuPrefs.delete(userId)
      }
    })()

    inFlightMenuPrefs.set(userId, requestPromise)
    return requestPromise
  },

  getUserMenuPreference: async (userId: number, pageId: number): Promise<UserMenuPreference> => {
    const response = await apiClient.get(
      API_ENDPOINTS.PERMISSIONS.USER_MENU_PREFERENCES.GET_BY_PAGE(userId, pageId)
    )
    return extractData<UserMenuPreference>(response)
  },

  createOrUpdateUserMenuPreference: async (
    userId: number,
    data: UserMenuPreferenceCreateRequest
  ): Promise<UserMenuPreference> => {
    const response = await apiClient.post(
      API_ENDPOINTS.PERMISSIONS.USER_MENU_PREFERENCES.CREATE_OR_UPDATE(userId),
      data
    )
    return extractData<UserMenuPreference>(response)
  },

  bulkUpdateUserMenuPreferences: async (
    userId: number,
    data: UserMenuPreferenceBulkRequest
  ): Promise<UserMenuPreference[]> => {
    const response = await apiClient.put(
      API_ENDPOINTS.PERMISSIONS.USER_MENU_PREFERENCES.BULK_UPDATE(userId),
      data
    )
    return extractData<UserMenuPreference[]>(response)
  },

  deleteUserMenuPreference: async (userId: number, pageId: number): Promise<void> => {
    await apiClient.delete(
      API_ENDPOINTS.PERMISSIONS.USER_MENU_PREFERENCES.DELETE(userId, pageId)
    )
  },
}

