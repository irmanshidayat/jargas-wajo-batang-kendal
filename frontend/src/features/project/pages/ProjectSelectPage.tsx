import React, { useEffect, useState } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { fetchUserProjects, selectProject } from '@/store/slices/projectSlice'
import ProjectCard from '../components/ProjectCard'
import ProjectFormModal from '../components/ProjectFormModal'
import Button from '@/components/common/Button'
import type { Project } from '../types'
import Swal from 'sweetalert2'

const ProjectSelectPage: React.FC = () => {
  const dispatch = useAppDispatch()
  const { availableProjects, isLoading } = useAppSelector((state) => state.project)
  const { isAuthenticated } = useAppSelector((state) => state.auth)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    // Navigasi akan di-handle oleh PublicRoute/PrivateRoute
    // Tidak perlu check isAuthenticated dan navigate manual untuk menghindari redundansi
    if (isAuthenticated) {
      dispatch(fetchUserProjects())
    }
  }, [dispatch, isAuthenticated])

  const handleSelectProject = async (project: Project) => {
    try {
      await dispatch(selectProject(project)).unwrap()
      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: `Project "${project.name}" dipilih`,
        timer: 1500,
        showConfirmButton: false,
      })
      // Navigasi akan di-handle oleh PrivateRoute setelah currentProject berubah
      // Tidak perlu navigate manual untuk menghindari redundansi
    } catch (error: any) {
      await Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error || 'Gagal memilih project',
      })
    }
  }

  const handleCreateSuccess = () => {
    dispatch(fetchUserProjects())
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-3">
            Pilih Project
          </h1>
          <p className="text-slate-600 text-lg">
            Pilih project yang ingin Anda gunakan atau buat project baru
          </p>
        </div>

        <div className="mb-6 flex justify-center">
          <Button
            onClick={() => setShowCreateModal(true)}
            variant="primary"
            size="lg"
          >
            + Buat Project Baru
          </Button>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : availableProjects.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md p-12 text-center">
            <p className="text-slate-600 text-lg mb-4">
              Anda belum memiliki project
            </p>
            <Button
              onClick={() => setShowCreateModal(true)}
              variant="primary"
            >
              Buat Project Pertama
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {availableProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onSelect={handleSelectProject}
                isLoading={isLoading}
              />
            ))}
          </div>
        )}

        <ProjectFormModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateSuccess}
        />
      </div>
    </div>
  )
}

export default ProjectSelectPage

