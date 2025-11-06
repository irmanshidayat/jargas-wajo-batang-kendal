import { createBrowserRouter, Navigate } from 'react-router-dom'
import PrivateRoute from './PrivateRoute'
import PublicRoute from './PublicRoute'
import Layout from '@/components/layout'
import LoginPage from '@/features/auth/components/LoginForm'
import DashboardPage from '@/features/dashboard/pages/DashboardPage'
import InventoryDashboardPage from '@/features/inventory/pages/InventoryDashboardPage'
import StockInPage from '@/features/inventory/pages/StockInPage'
import StockOutPage from '@/features/inventory/pages/StockOutPage'
import MaterialsPage from '@/features/inventory/pages/MaterialsPage'
import MandorsPage from '@/features/inventory/pages/MandorsPage'
import ReturnsPage from '@/features/inventory/pages/ReturnsPage'
import ReturnsListPage from '@/features/inventory/pages/ReturnsListPage'
import StockInListPage from '@/features/inventory/pages/StockInListPage'
import StockOutListPage from '@/features/inventory/pages/StockOutListPage'
import InstalledPage from '@/features/inventory/pages/InstalledPage'
import InstalledListPage from '@/features/inventory/pages/InstalledListPage'
import SuratPermintaanPage from '@/features/inventory/pages/SuratPermintaanPage'
import SuratPermintaanListPage from '@/features/inventory/pages/SuratPermintaanListPage'
import UserManagementMainPage from '@/features/user-management/pages/UserManagementMainPage'
import UsersManagementPage from '@/features/user-management/pages/UsersManagementPage'
import RolesManagementPage from '@/features/user-management/pages/RolesManagementPage'
import PermissionsManagementPage from '@/features/user-management/pages/PermissionsManagementPage'
import ProjectSelectPage from '@/features/project/pages/ProjectSelectPage'
 

export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: '/select-project',
    element: (
      <PrivateRoute>
        <ProjectSelectPage />
      </PrivateRoute>
    ),
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <PrivateRoute>
            <DashboardPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory',
        element: (
          <PrivateRoute requiredPermission="read">
            <InventoryDashboardPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/stock-out/list',
        element: (
          <PrivateRoute requiredPermission="read">
            <StockOutListPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/stock-in/list',
        element: (
          <PrivateRoute requiredPermission="read">
            <StockInListPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/stock-in',
        element: (
          <PrivateRoute requiredPermission="read">
            <StockInPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/stock-out',
        element: (
          <PrivateRoute requiredPermission="read">
            <StockOutPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/materials',
        element: (
          <PrivateRoute requiredPermission="read">
            <MaterialsPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/mandors',
        element: (
          <PrivateRoute requiredPermission="read">
            <MandorsPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/returns',
        element: (
          <PrivateRoute requiredPermission="read">
            <ReturnsListPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/returns/create',
        element: (
          <PrivateRoute requiredPermission="read">
            <ReturnsPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/installed/list',
        element: <Navigate to="/inventory/installed" replace />,
      },
      {
        path: 'inventory/installed',
        element: (
          <PrivateRoute requiredPermission="read">
            <InstalledListPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/installed/create',
        element: (
          <PrivateRoute requiredPermission="read">
            <InstalledPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/surat-permintaan',
        element: (
          <PrivateRoute requiredPermission="read">
            <SuratPermintaanPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'inventory/surat-permintaan/list',
        element: (
          <PrivateRoute requiredPermission="read">
            <SuratPermintaanListPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'user-management',
        element: (
          <PrivateRoute requiredPermission="read">
            <UserManagementMainPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'user-management/users',
        element: (
          <PrivateRoute requiredPermission="read">
            <UsersManagementPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'user-management/roles',
        element: (
          <PrivateRoute requiredPermission="read">
            <RolesManagementPage />
          </PrivateRoute>
        ),
      },
      {
        path: 'user-management/permissions',
        element: (
          <PrivateRoute requiredPermission="read">
            <PermissionsManagementPage />
          </PrivateRoute>
        ),
      },
    ],
  },
])
