import React from 'react'
import type { Project } from '../types'
import Button from '@/components/common/Button'

interface ProjectCardProps {
  project: Project
  onSelect: (project: Project) => void
  isLoading?: boolean
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project, onSelect, isLoading = false }) => {
  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 p-6 border border-slate-200">
      <div className="flex flex-col h-full">
        <div className="flex-1">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-xl font-bold text-slate-900">{project.name}</h3>
            {project.is_owner && (
              <span className="px-2 py-1 text-xs font-semibold bg-indigo-100 text-indigo-800 rounded-full">
                Owner
              </span>
            )}
          </div>
          {project.code && (
            <p className="text-sm text-slate-600 mb-2">
              <span className="font-medium">Kode:</span> {project.code}
            </p>
          )}
          {project.description && (
            <p className="text-sm text-slate-500 line-clamp-2 mb-4">
              {project.description}
            </p>
          )}
        </div>
        <Button
          onClick={() => onSelect(project)}
          disabled={isLoading}
          className="w-full mt-auto"
          variant="primary"
        >
          Pilih Project
        </Button>
      </div>
    </div>
  )
}

export default ProjectCard

