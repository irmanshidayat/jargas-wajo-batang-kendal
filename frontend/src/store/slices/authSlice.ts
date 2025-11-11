import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { authService } from '@/features/auth/services/authService'

interface Permission {
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

interface Role {
  id: number
  name: string
  description?: string
}

interface User {
  id: number
  email: string
  name: string
  is_active: boolean
  is_superuser?: boolean
  role?: Role
  permissions: Permission[]
}

type PermissionsStatus = 'idle' | 'loading' | 'succeeded' | 'failed'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  permissionsStatus: PermissionsStatus
}

const savedUserRaw = typeof window !== 'undefined' ? localStorage.getItem('user') : null
const savedUser: User | null = savedUserRaw ? (() => {
  try {
    const parsed = JSON.parse(savedUserRaw) as User
    // Ensure permissions array exists (bukan null atau undefined)
    if (!parsed.permissions || !Array.isArray(parsed.permissions)) {
      parsed.permissions = []
    }
    return parsed
  } catch {
    return null
  }
})() : null

const savedToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null

// Set isAuthenticated ke false di initial state
// Token akan di-validate saat app load di App.tsx atau Layout.tsx
// Ini untuk memastikan user harus login dulu jika token tidak valid
const initialIsAuthenticated = false

// Set initial permissionsStatus berdasarkan apakah user sudah ada
// Jika user ada dari localStorage, set status ke 'idle' (akan di-refresh di Layout)
// Jika tidak ada user, tetap 'idle'
const initialPermissionsStatus: 'idle' | 'loading' | 'succeeded' | 'failed' = 
  savedUser ? 'idle' : 'idle'

const initialState: AuthState = {
  user: savedUser,
  token: savedToken,
  // Hanya set isAuthenticated = true jika ada token DAN user yang valid
  // Jika tidak, user harus login dulu untuk mendapatkan token dan user yang valid
  isAuthenticated: initialIsAuthenticated,
  isLoading: false,
  error: null,
  permissionsStatus: initialPermissionsStatus,
}

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const loginResponse = await authService.login(credentials)
      const { token, user } = loginResponse
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      return { token, user }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || error.message || 'Login gagal')
    }
  }
)

export const logout = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  await authService.logout()
})

/**
 * Validate token dengan cara fetch user profile
 * Jika berhasil, berarti token masih valid
 * Jika gagal (401), berarti token expired atau invalid
 */
export const validateToken = createAsyncThunk(
  'auth/validateToken',
  async (_, { rejectWithValue }) => {
    try {
      const { authService } = await import('@/features/auth/services/authService')
      const user = await authService.getProfile()
      // Update localStorage dengan user terbaru
      localStorage.setItem('user', JSON.stringify(user))
      return user
    } catch (error: any) {
      // Skip CanceledError - ini expected behavior saat cancel duplicate request
      // Request di-cancel karena duplicate, tidak perlu handle sebagai error
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message === 'canceled') {
        // Request di-cancel karena duplicate, request baru yang sedang berjalan akan handle hasilnya
        // Return reject dengan special flag untuk skip error handling
        return rejectWithValue('CANCELED')
      }
      
      // Jika error 401, berarti token expired atau invalid
      if (error.response?.status === 401) {
        // Clear invalid token dan user
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('currentProject')
      }
      const errorMessage = error.response?.data?.message || error.message || 'Token tidak valid'
      return rejectWithValue(errorMessage)
    }
  },
  {
    // Redux Toolkit option untuk handle deduplication
    // condition: check apakah sudah ada pending request
    // Jika return false, Redux akan skip dispatch dan return existing promise
    condition: (_, { getState }) => {
      const state = getState() as { auth: AuthState }
      // Skip jika sedang loading (Redux akan return existing promise dari dispatch sebelumnya)
      if (state.auth.isLoading) {
        console.log('[AuthSlice] Validate token sudah berjalan, skip duplicate call')
        return false // Skip dispatch, Redux akan return existing promise
      }
      return true // Allow dispatch
    },
  }
)

export const refreshUserPermissions = createAsyncThunk(
  'auth/refreshPermissions',
  async (_, { rejectWithValue }) => {
    try {
      const { authService } = await import('@/features/auth/services/authService')
      const user = await authService.refreshPermissions()
      // Update localStorage
      localStorage.setItem('user', JSON.stringify(user))
      return user
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || 'Gagal refresh permissions'
      return rejectWithValue(errorMessage)
    }
  },
  {
    // Redux Toolkit option untuk handle deduplication
    // condition: check apakah sudah ada pending request
    // Jika return false, Redux akan skip dispatch dan return existing promise
    condition: (_, { getState }) => {
      const state = getState() as { auth: AuthState }
      // Skip jika sedang loading (Redux akan return existing promise dari dispatch sebelumnya)
      if (state.auth.permissionsStatus === 'loading') {
        console.log('[AuthSlice] Refresh permissions sudah berjalan, skip duplicate call')
        return false // Skip dispatch, Redux akan return existing promise
      }
      return true // Allow dispatch
    },
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
      state.isAuthenticated = true
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        state.token = action.payload.token
        // Ensure user has permissions array (bukan null atau undefined)
        const user = action.payload.user
        if (user && (!user.permissions || !Array.isArray(user.permissions))) {
          user.permissions = []
        }
        state.user = user
        // Set permissions status ke 'succeeded' jika user sudah punya permissions dari login response
        // Jika tidak, set ke 'idle' agar di-refresh di Layout
        if (user && Array.isArray(user.permissions) && user.permissions.length > 0) {
          state.permissionsStatus = 'succeeded'
        } else {
          // Permissions akan di-refresh di Layout component
          state.permissionsStatus = 'idle'
        }
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(refreshUserPermissions.pending, (state) => {
        // Set status loading untuk prevent multiple calls
        state.permissionsStatus = 'loading'
        state.error = null
      })
      .addCase(refreshUserPermissions.fulfilled, (state, action) => {
        // Update user dengan permissions terbaru
        const user = action.payload
        if (user && !user.permissions) {
          user.permissions = []
        }
        state.user = user
        state.permissionsStatus = 'succeeded'
      })
      .addCase(refreshUserPermissions.rejected, (state, action) => {
        // Set status failed untuk prevent infinite retry
        state.permissionsStatus = 'failed'
        // Log error tapi tidak perlu mengganggu user
        console.error('Failed to refresh permissions:', action.payload)
      })
      .addCase(validateToken.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(validateToken.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        // Update user dengan data terbaru dari server
        const user = action.payload
        if (user && (!user.permissions || !Array.isArray(user.permissions))) {
          user.permissions = []
        }
        state.user = user
        // Set permissions status berdasarkan apakah user punya permissions
        if (user && Array.isArray(user.permissions) && user.permissions.length > 0) {
          state.permissionsStatus = 'succeeded'
        } else {
          state.permissionsStatus = 'idle'
        }
      })
      .addCase(validateToken.rejected, (state, action) => {
        state.isLoading = false
        
        // Skip error handling jika request di-cancel (duplicate request)
        // Ini expected behavior untuk request deduplication
        if (action.payload === 'CANCELED') {
          // Request di-cancel karena duplicate, tidak perlu update state
          // Request baru yang sedang berjalan akan handle hasilnya
          return
        }
        
        // Hanya update state jika benar-benar error (bukan canceled)
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.permissionsStatus = 'idle'
        // Log error untuk debugging (hanya untuk error yang bukan canceled)
        console.error('Token validation failed:', action.payload)
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.isAuthenticated = false
        state.permissionsStatus = 'idle'
      })
  },
})

export const { setUser, clearError } = authSlice.actions
export default authSlice.reducer
