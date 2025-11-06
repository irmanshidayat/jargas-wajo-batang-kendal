import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { API_BASE_URL } from '@/utils/constants'
import Swal from 'sweetalert2'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 detik (diperpanjang dari 10 detik)
})

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add project ID header if available
    const currentProject = localStorage.getItem('currentProject')
    if (currentProject && config.headers) {
      try {
        const project = JSON.parse(currentProject)
        if (project?.id) {
          config.headers['X-Project-ID'] = String(project.id)
        }
      } catch (e) {
        // Ignore parse errors
      }
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status
      const responseData = error.response.data as any

      // Log error untuk debugging
      console.error('API Error:', {
        status,
        url: error.config?.url,
        data: responseData,
        errors: responseData?.errors
      })

      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('currentProject')
        window.location.href = '/login'
        await Swal.fire({
          icon: 'error',
          title: 'Sesi Berakhir',
          text: 'Silakan login kembali',
          confirmButtonText: 'OK',
        })
      } else if (status === 422) {
        // Unprocessable Entity - Validation Error
        const errorMessage = responseData?.message || 'Validasi data gagal'
        const errors = responseData?.errors || {}
        const errorDetails = Object.keys(errors).length > 0 
          ? Object.entries(errors).map(([key, value]) => `${key}: ${value}`).join('\n')
          : errorMessage
        
        console.error('Validation Error Details:', errors)
        await Swal.fire({
          icon: 'error',
          title: 'Validasi Gagal',
          text: errorDetails,
          confirmButtonText: 'OK',
        })
      } else if (status >= 500) {
        await Swal.fire({
          icon: 'error',
          title: 'Error Server',
          text: 'Terjadi kesalahan pada server. Silakan coba lagi nanti.',
          confirmButtonText: 'OK',
        })
      }
    } else if (error.request) {
      await Swal.fire({
        icon: 'error',
        title: 'Tidak Ada Koneksi',
        text: 'Periksa koneksi internet Anda.',
        confirmButtonText: 'OK',
      })
    }

    return Promise.reject(error)
  }
)

export default apiClient
