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
      const url = error.config?.url || 'unknown'

      // Log error untuk debugging dengan detail lengkap di console browser
      console.group('🚨 API Error')
      console.error('Status:', status)
      console.error('URL:', url)
      console.error('Method:', error.config?.method?.toUpperCase())
      console.error('Base URL:', error.config?.baseURL)
      console.error('Response Data:', responseData)
      if (responseData?.errors) {
        console.error('Validation Errors:', responseData.errors)
      }
      if (responseData?.detail) {
        console.error('Error Detail:', responseData.detail)
      }
      console.error('Full Error Object:', error)
      console.groupEnd()

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
        
        console.group('⚠️ Validation Error')
        console.error('Errors:', errors)
        console.error('Full Response:', responseData)
        console.groupEnd()
        await Swal.fire({
          icon: 'error',
          title: 'Validasi Gagal',
          text: errorDetails,
          confirmButtonText: 'OK',
        })
      } else if (status >= 500) {
        // Server Error - tampilkan detail error jika ada
        const errorMessage = responseData?.message || responseData?.detail || 'Terjadi kesalahan pada server'
        const errorDetail = responseData?.detail || responseData?.error || 'Silakan coba lagi nanti atau hubungi administrator'
        
        console.group('❌ Server Error (500+)')
        console.error('Message:', errorMessage)
        console.error('Detail:', errorDetail)
        console.error('URL:', url)
        console.error('Full Response:', responseData)
        console.error('Full Error:', error)
        console.groupEnd()

        await Swal.fire({
          icon: 'error',
          title: 'Error Server (500)',
          html: `
            <div style="text-align: left;">
              <p><strong>Pesan:</strong> ${errorMessage}</p>
              <p><strong>Detail:</strong> ${errorDetail}</p>
              <p style="margin-top: 10px; font-size: 12px; color: #666;">
                URL: ${url}<br/>
                Periksa console browser untuk detail lebih lengkap.
              </p>
            </div>
          `,
          confirmButtonText: 'OK',
          width: '600px'
        })
      }
    } else if (error.request) {
      // Request dibuat tapi tidak ada response (connection error)
      const isConnectionRefused = error.code === 'ECONNREFUSED' || 
                                   error.message?.includes('ECONNREFUSED') ||
                                   error.message?.includes('Network Error')
      
      const errorMessage = isConnectionRefused
        ? 'Backend server tidak berjalan atau tidak dapat diakses. Pastikan backend server sudah berjalan di port 8000 atau 8001.'
        : 'Tidak dapat terhubung ke server. Periksa koneksi internet Anda atau pastikan server sudah berjalan.'

      console.group('🔌 Connection Error')
      console.error('Code:', error.code)
      console.error('Message:', error.message)
      console.error('URL:', error.config?.url)
      console.error('Base URL:', error.config?.baseURL)
      console.error('Full Error:', error)
      console.groupEnd()

      await Swal.fire({
        icon: 'error',
        title: 'Tidak Ada Koneksi',
        html: `
          <div style="text-align: left;">
            <p>${errorMessage}</p>
            <p style="margin-top: 10px; font-size: 12px; color: #666;">
              <strong>Tips:</strong><br/>
              • Jika menggunakan Docker: jalankan <code>docker-compose up -d backend</code><br/>
              • Jika tidak menggunakan Docker: jalankan <code>python run.py</code> di folder backend<br/>
              • Pastikan backend berjalan di port 8000 atau 8001
            </p>
          </div>
        `,
        confirmButtonText: 'OK',
        width: '600px'
      })
    } else {
      // Error lainnya
      console.group('❓ Unknown Error')
      console.error('Error:', error)
      console.error('Message:', error.message)
      console.error('Stack:', error.stack)
      console.groupEnd()
      await Swal.fire({
        icon: 'error',
        title: 'Terjadi Kesalahan',
        text: error.message || 'Terjadi kesalahan yang tidak diketahui. Periksa console untuk detail.',
        confirmButtonText: 'OK',
      })
    }

    return Promise.reject(error)
  }
)

export default apiClient
