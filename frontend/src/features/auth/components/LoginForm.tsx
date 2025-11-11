import React, { useState } from 'react'
import { useAppDispatch } from '@/store/hooks'
import { login } from '@/store/slices/authSlice'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import Swal from 'sweetalert2'

const LoginForm: React.FC = () => {
  const dispatch = useAppDispatch()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!email || !password) {
      await Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Email dan password harus diisi',
      })
      return
    }

    try {
      setLoading(true)
      await dispatch(login({ email, password })).unwrap()
      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Login berhasil!',
        timer: 1500,
        showConfirmButton: false,
      })
      // Navigasi akan di-handle oleh PublicRoute setelah state isAuthenticated berubah
      // Tidak perlu navigate manual untuk menghindari redundansi
    } catch (err: any) {
      await Swal.fire({
        icon: 'error',
        title: 'Login Gagal',
        text: err || 'Email atau password salah',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-md w-full bg-white rounded-xl shadow-2xl p-8 md:p-10 border border-slate-200">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-2">Login</h1>
          <p className="text-slate-600">Masuk ke akun Anda</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="masukkan email"
            required
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="masukkan password"
            required
          />

          <Button
            type="submit"
            className="w-full"
            disabled={loading}
          >
            {loading ? 'Memproses...' : 'Login'}
          </Button>
        </form>
      </div>
    </div>
  )
}

export default LoginForm
