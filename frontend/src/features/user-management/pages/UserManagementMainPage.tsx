import React from 'react'
import { Link } from 'react-router-dom'
import { ROUTES } from '@/utils/constants'

const UserManagementMainPage: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">User dan Role Management</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to={ROUTES.USER_MANAGEMENT_USERS}
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-semibold mb-2">Users</h2>
          <p className="text-gray-600">Kelola users, assign role dan permissions</p>
        </Link>
        
        <Link
          to={ROUTES.USER_MANAGEMENT_ROLES}
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-semibold mb-2">Roles</h2>
          <p className="text-gray-600">Kelola roles dan assign permissions</p>
        </Link>
        
        <Link
          to={ROUTES.USER_MANAGEMENT_PERMISSIONS}
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-semibold mb-2">Permissions</h2>
          <p className="text-gray-600">Kelola permissions dengan matrix CRUD</p>
        </Link>
      </div>
    </div>
  )
}

export default UserManagementMainPage

