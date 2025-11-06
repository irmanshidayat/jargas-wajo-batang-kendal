import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { authService } from '@/features/auth/services/authService'

interface Permission {
  id: number
  page_id: number
  page_name?: string
  page_path?: string
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

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

const savedUserRaw = typeof window !== 'undefined' ? localStorage.getItem('user') : null
const savedUser: User | null = savedUserRaw ? (() => {
  try {
    const parsed = JSON.parse(savedUserRaw) as User
    // Ensure permissions array exists
    if (!parsed.permissions) {
      parsed.permissions = []
    }
    return parsed
  } catch {
    return null
  }
})() : null

const initialState: AuthState = {
  user: savedUser,
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem('token') : false,
  isLoading: false,
  error: null,
}

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const loginResponse = await authService.login(credentials)
      console.log('[DEBUG] API Login Response:', loginResponse)
      const { token, user } = loginResponse
      console.log('[DEBUG] Token:', token)
      console.log('[DEBUG] User:', user)
      console.log('[DEBUG] User Permissions Count:', user?.permissions?.length)
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      return { token, user }
    } catch (error: any) {
      console.log('[DEBUG] Login error:', error)
      return rejectWithValue(error.response?.data?.message || error.message || 'Login gagal')
    }
  }
)

export const logout = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  await authService.logout()
})

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
      return rejectWithValue(error.response?.data?.message || 'Gagal refresh permissions')
    }
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
        // Ensure user has permissions array
        const user = action.payload.user
        if (user && !user.permissions) {
          user.permissions = []
        }
        state.user = user
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(refreshUserPermissions.pending, (state) => {
        // Tidak set isLoading agar tidak mengganggu UI
        state.error = null
      })
      .addCase(refreshUserPermissions.fulfilled, (state, action) => {
        // Update user dengan permissions terbaru
        const user = action.payload
        if (user && !user.permissions) {
          user.permissions = []
        }
        state.user = user
      })
      .addCase(refreshUserPermissions.rejected, (state, action) => {
        // Log error tapi tidak perlu mengganggu user
        console.error('Failed to refresh permissions:', action.payload)
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.isAuthenticated = false
      })
  },
})

export const { setUser, clearError } = authSlice.actions
export default authSlice.reducer
