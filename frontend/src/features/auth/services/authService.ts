import { apiClient, API_ENDPOINTS } from '@/services/api'
import { extractData } from '@/utils/api'
import type { LoginRequest, LoginResponse } from '../types'

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, credentials)
    return extractData<LoginResponse>(response)
  },

  logout: async (): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT)
  },

  getProfile: async (): Promise<LoginResponse['user']> => {
    const response = await apiClient.get(API_ENDPOINTS.AUTH.PROFILE)
    return extractData<LoginResponse['user']>(response)
  },

  refreshPermissions: async (): Promise<LoginResponse['user']> => {
    const response = await apiClient.get(API_ENDPOINTS.AUTH.PROFILE)
    return extractData<LoginResponse['user']>(response)
  },
}
