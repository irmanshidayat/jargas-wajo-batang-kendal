import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { projectService } from '@/features/project/services/projectService'
import type { Project } from '@/features/project/types'

interface ProjectState {
  currentProject: Project | null
  availableProjects: Project[]
  isLoading: boolean
  error: string | null
}

const savedProject = typeof window !== 'undefined' 
  ? (() => {
      try {
        const saved = localStorage.getItem('currentProject')
        return saved ? JSON.parse(saved) : null
      } catch {
        return null
      }
    })()
  : null

const initialState: ProjectState = {
  currentProject: savedProject,
  availableProjects: [],
  isLoading: false,
  error: null,
}

export const fetchUserProjects = createAsyncThunk(
  'project/fetchUserProjects',
  async (_, { rejectWithValue }) => {
    try {
      const response = await projectService.getUserProjects()
      return response.projects
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Gagal mengambil daftar project')
    }
  }
)

export const selectProject = createAsyncThunk(
  'project/selectProject',
  async (project: Project, { rejectWithValue }) => {
    try {
      // Save to localStorage
      localStorage.setItem('currentProject', JSON.stringify(project))
      return project
    } catch (error: any) {
      return rejectWithValue('Gagal menyimpan project')
    }
  }
)

export const clearProject = createAsyncThunk(
  'project/clearProject',
  async () => {
    localStorage.removeItem('currentProject')
  }
)

const projectSlice = createSlice({
  name: 'project',
  initialState,
  reducers: {
    setCurrentProject: (state, action: PayloadAction<Project>) => {
      state.currentProject = action.payload
      localStorage.setItem('currentProject', JSON.stringify(action.payload))
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserProjects.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchUserProjects.fulfilled, (state, action) => {
        state.isLoading = false
        state.availableProjects = action.payload
      })
      .addCase(fetchUserProjects.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(selectProject.fulfilled, (state, action) => {
        state.currentProject = action.payload
      })
      .addCase(clearProject.fulfilled, (state) => {
        state.currentProject = null
      })
  },
})

export const { setCurrentProject, clearError } = projectSlice.actions
export default projectSlice.reducer

