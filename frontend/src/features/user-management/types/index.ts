export interface Role {
  id: number
  name: string
  description?: string
  created_at: string
  updated_at: string
}

export interface Page {
  id: number
  name: string
  path: string
  icon?: string
  display_name: string
  order: number
  created_at: string
  updated_at: string
}

export interface Permission {
  id: number
  page_id: number
  page_name?: string
  page_path?: string
  can_create: boolean
  can_read: boolean
  can_update: boolean
  can_delete: boolean
  created_at: string
  updated_at: string
}

export interface PermissionDetail extends Permission {
  page?: Page
}

export interface RoleDetail extends Role {
  permissions: Permission[]
}

export interface User {
  id: number
  email: string
  name: string
  is_active: boolean
  is_superuser: boolean
  role_id?: number
  role?: Role
  created_at: string
  updated_at: string
}

export interface RoleCreateRequest {
  name: string
  description?: string
}

export interface RoleUpdateRequest {
  name?: string
  description?: string
}

export interface PageCreateRequest {
  name: string
  path: string
  icon?: string
  display_name: string
  order?: number
}

export interface PageUpdateRequest {
  name?: string
  path?: string
  icon?: string
  display_name?: string
  order?: number
}

export interface PermissionCreateRequest {
  page_id: number
  can_create: boolean
  can_read: boolean
  can_update: boolean
  can_delete: boolean
}

export interface PermissionUpdateRequest {
  can_create?: boolean
  can_read?: boolean
  can_update?: boolean
  can_delete?: boolean
}

export interface AssignPermissionsRequest {
  permission_ids: number[]
}

export interface PageCRUDPermission {
  page_id: number
  can_create: boolean
  can_read: boolean
  can_update: boolean
  can_delete: boolean
}

export interface AssignRolePermissionsCRUDRequest {
  page_permissions: PageCRUDPermission[]
}

export interface UserCreateRequest {
  email: string
  name: string
  password: string
  role_id?: number
  is_active?: boolean
  is_superuser?: boolean
}

export interface UserUpdateRequest {
  email?: string
  name?: string
  role_id?: number
  is_active?: boolean
  is_superuser?: boolean
}

export interface UserMenuPreference {
  id: number
  user_id: number
  page_id: number
  show_in_menu: boolean
  created_at: string
  updated_at: string
  page?: Page
}

export interface UserMenuPreferenceCreateRequest {
  page_id: number
  show_in_menu: boolean
}

export interface UserMenuPreferenceBulkRequest {
  preferences: Array<{
    page_id: number
    show_in_menu: boolean
  }>
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  message: string
}

