import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboardService } from '../services/dashboardService'
import type { DashboardStats } from '../types'
import Swal from 'sweetalert2'

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const data = await dashboardService.getStats()
        setStats(data)
      } catch (error: any) {
        await Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.message || 'Gagal memuat data dashboard',
        })
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    // Refresh setiap 30 detik
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
          <p className="text-slate-700 font-medium">Memuat data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard Jargas APBN</h1>
        <p className="text-gray-600 mt-1">Ringkasan data dan statistik sistem inventory</p>
      </div>

      {/* Main Summary Cards */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 rounded-2xl shadow-2xl p-8 text-white overflow-hidden relative">
        <div className="relative z-10">
          <h2 className="text-2xl font-bold mb-2">Ringkasan Umum</h2>
          <p className="text-indigo-100 mb-6">Statistik data inventory Jargas APBN</p>

          {/* Glass Effect Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white/20 backdrop-blur-md rounded-xl p-5 border border-white/30 shadow-lg hover:bg-white/30 transition-all">
              <div className="flex items-center justify-between mb-2">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center shadow-md">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{stats?.total_materials || 0}</p>
              <p className="text-indigo-100 text-sm">Total Barang</p>
            </div>

            <div className="bg-white/20 backdrop-blur-md rounded-xl p-5 border border-white/30 shadow-lg hover:bg-white/30 transition-all">
              <div className="flex items-center justify-between mb-2">
                <div className="w-12 h-12 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center shadow-md">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{stats?.total_mandors || 0}</p>
              <p className="text-indigo-100 text-sm">Total Mandor</p>
            </div>

            <div className="bg-white/20 backdrop-blur-md rounded-xl p-5 border border-white/30 shadow-lg hover:bg-white/30 transition-all">
              <div className="flex items-center justify-between mb-2">
                <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-lg flex items-center justify-center shadow-md">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{stats?.total_stock_current || 0}</p>
              <p className="text-indigo-100 text-sm">Stock Saat Ini</p>
            </div>

            <div className="bg-white/20 backdrop-blur-md rounded-xl p-5 border border-white/30 shadow-lg hover:bg-white/30 transition-all">
              <div className="flex items-center justify-between mb-2">
                <div className="w-12 h-12 bg-gradient-to-br from-rose-400 to-pink-500 rounded-lg flex items-center justify-center shadow-md">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                </div>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{stats?.unread_notifications || 0}</p>
              <p className="text-indigo-100 text-sm">Notifikasi</p>
            </div>
          </div>
        </div>
        {/* Decorative Background */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-pink-400/20 rounded-full blur-3xl"></div>
      </div>

      {/* Activity This Month */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-md p-6 border border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Barang Masuk</h3>
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-bold text-blue-600 mb-2">{stats?.total_stock_in_month || 0}</p>
          <p className="text-sm text-gray-500">Bulan ini</p>
          <Link 
            to="/inventory/stock-in" 
            className="text-blue-600 text-sm font-medium hover:text-blue-700 mt-4 inline-block"
          >
            Lihat detail →
          </Link>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Barang Keluar</h3>
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-bold text-red-600 mb-2">{stats?.total_stock_out_month || 0}</p>
          <p className="text-sm text-gray-500">Bulan ini</p>
          <Link 
            to="/inventory/stock-out" 
            className="text-red-600 text-sm font-medium hover:text-red-700 mt-4 inline-block"
          >
            Lihat detail →
          </Link>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Discrepancies</h3>
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-bold text-yellow-600 mb-2">{stats?.active_discrepancies || 0}</p>
          <p className="text-sm text-gray-500">Perlu perhatian</p>
          {stats && stats.active_discrepancies > 0 && (
            <Link 
              to="/inventory" 
              className="text-yellow-600 text-sm font-medium hover:text-yellow-700 mt-4 inline-block"
            >
              Lihat detail →
            </Link>
          )}
        </div>
      </div>

      {/* Quick Links */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-slate-200">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">
          Menu Cepat
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link 
            to="/inventory" 
            className="flex items-center p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span className="text-gray-700 font-medium">Dashboard Inventory</span>
          </Link>
          <Link 
            to="/inventory/materials" 
            className="flex items-center p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <span className="text-gray-700 font-medium">Data Barang</span>
          </Link>
          <Link 
            to="/inventory/mandors" 
            className="flex items-center p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <span className="text-gray-700 font-medium">Data Mandor</span>
          </Link>
          <Link 
            to="/inventory/returns" 
            className="flex items-center p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <span className="text-gray-700 font-medium">Barang Kembali</span>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage

