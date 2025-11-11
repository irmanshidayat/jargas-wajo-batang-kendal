export interface LoginRequest {
  email: string
  password: string
}

export interface Permission {
  id: number
  page_id: number
  page_name?: string
  page_path?: string
  display_name?: string
  can_create: boolean
  can_read: boolean
  can_update: boolean
  can_delete: boolean
}

export interface Role {
  id: number
  name: string
  description?: string
}

export interface LoginResponse {
  token: string
  user: {
    id: number
    email: string
    name: string
    is_active: boolean
    role?: Role
    permissions: Permission[]
  }
}
