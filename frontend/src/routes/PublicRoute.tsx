import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'

interface PublicRouteProps {
  children: React.ReactNode
}

const PublicRoute = ({ children }: PublicRouteProps) => {
  const { isAuthenticated } = useAppSelector((state) => state.auth)
  const { currentProject } = useAppSelector((state) => state.project)

  if (isAuthenticated) {
    // Jika sudah login tapi belum pilih project, redirect ke select-project
    if (!currentProject) {
      return <Navigate to="/select-project" replace />
    }
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

export default PublicRoute
