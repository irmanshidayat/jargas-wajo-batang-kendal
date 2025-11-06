export interface Project {
  id: number
  name: string
  code: string | null
  description: string | null
  is_active: boolean
  is_owner?: boolean
  created_at: string
  updated_at: string
}

export interface ProjectCreateRequest {
  name: string
  code?: string | null
  description?: string | null
}

export interface ProjectUpdateRequest {
  name?: string
  code?: string | null
  description?: string | null
  is_active?: boolean
}

export interface ProjectsResponse {
  projects: Project[]
  total: number
}

