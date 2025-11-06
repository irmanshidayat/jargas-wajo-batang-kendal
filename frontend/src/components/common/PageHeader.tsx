import React, { ReactNode } from 'react'

interface PageHeaderProps {
  title: string
  description?: string
  actionButton?: ReactNode
}

const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  actionButton,
}) => {
  return (
    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg shadow-lg p-6 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">
            {title}
          </h1>
          {description && (
            <p className="text-indigo-100 text-sm sm:text-base">
              {description}
            </p>
          )}
        </div>
        {actionButton && <div className="mt-4 sm:mt-0">{actionButton}</div>}
      </div>
    </div>
  )
}

export default PageHeader

