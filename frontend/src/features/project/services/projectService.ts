import { apiClient, API_ENDPOINTS } from '@/services/api'
import { extractData, extractPaginatedResponse } from '@/utils/api'
import type { Project, ProjectCreateRequest, ProjectsResponse } from '../types'

export const projectService = {
  async getUserProjects(): Promise<ProjectsResponse> {
    const response = await apiClient.get(API_ENDPOINTS.PROJECTS.MY_PROJECTS)
    return extractData<ProjectsResponse>(response)
  },

  async getAllProjects(page: number = 1, limit: number = 100) {
    const response = await apiClient.get(API_ENDPOINTS.PROJECTS.GET_ALL, {
      params: { page, limit },
    })
    return extractPaginatedResponse<Project>(response)
  },

  async getProjectById(id: number): Promise<Project> {
    const response = await apiClient.get(API_ENDPOINTS.PROJECTS.GET_BY_ID(id))
    return extractData<Project>(response)
  },

  async createProject(data: ProjectCreateRequest): Promise<Project> {
    const response = await apiClient.post(API_ENDPOINTS.PROJECTS.CREATE, data)
    return extractData<Project>(response)
  },

  async updateProject(id: number, data: Partial<ProjectCreateRequest>): Promise<Project> {
    const response = await apiClient.put(API_ENDPOINTS.PROJECTS.UPDATE(id), data)
    return extractData<Project>(response)
  },

  async deleteProject(id: number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.PROJECTS.DELETE(id))
  },
}

