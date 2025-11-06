import React, { useState, useEffect } from 'react'
import Swal from 'sweetalert2'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'
import type { Project, ProjectCreateRequest } from '../types'
import { projectService } from '../services/projectService'

interface ProjectFormModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  project?: Project | null
}

const ProjectFormModal: React.FC<ProjectFormModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  project = null,
}) => {
  const [formData, setFormData] = useState<ProjectCreateRequest>({
    name: '',
    code: '',
    description: '',
  })
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name,
        code: project.code || '',
        description: project.description || '',
      })
    } else {
      setFormData({
        name: '',
        code: '',
        description: '',
      })
    }
  }, [project, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.name.trim()) {
      await Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Nama project harus diisi',
      })
      return
    }

    try {
      setIsLoading(true)
      
      const dataToSend = {
        name: formData.name.trim(),
        code: formData.code?.trim() || null,
        description: formData.description?.trim() || null,
      }

      if (project) {
        await projectService.updateProject(project.id, dataToSend)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Project berhasil diupdate',
          timer: 1500,
          showConfirmButton: false,
        })
      } else {
        await projectService.createProject(dataToSend)
        await Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'Project berhasil dibuat',
          timer: 1500,
          showConfirmButton: false,
        })
      }

      onSuccess()
      onClose()
    } catch (error: any) {
      await Swal.fire({
        icon: 'error',
        title: 'Gagal',
        text: error.response?.data?.message || 'Terjadi kesalahan',
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
        <div className="p-6 border-b border-slate-200">
          <h2 className="text-2xl font-bold text-slate-900">
            {project ? 'Edit Project' : 'Buat Project Baru'}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <Input
            label="Nama Project"
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Masukkan nama project"
            required
          />

          <Input
            label="Kode Project (Opsional)"
            type="text"
            value={formData.code || ''}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            placeholder="Masukkan kode project"
          />

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Deskripsi (Opsional)
            </label>
            <textarea
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={3}
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Masukkan deskripsi project"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              className="flex-1"
              disabled={isLoading}
            >
              Batal
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              isLoading={isLoading}
            >
              {project ? 'Update' : 'Buat'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProjectFormModal

