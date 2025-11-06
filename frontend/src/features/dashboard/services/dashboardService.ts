import { apiClient, API_ENDPOINTS } from '@/services/api'
import { extractData } from '@/utils/api'
import type { DashboardStats } from '../types'

export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get(API_ENDPOINTS.DASHBOARD.STATS)
    return extractData<DashboardStats>(response)
  },
}
