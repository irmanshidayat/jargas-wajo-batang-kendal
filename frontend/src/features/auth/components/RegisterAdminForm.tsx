import React, { useState } from 'react'
import { useAppDispatch } from '@/store/hooks'
import { registerAdmin } from '@/store/slices/authSlice'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import Swal from 'sweetalert2'

const RegisterAdminForm: React.FC = () => {
  const dispatch = useAppDispatch()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<{
    name?: string
    email?: string
    password?: string
    confirmPassword?: string
  }>({})

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {}

    if (!name || name.trim().length < 3) {
      newErrors.name = 'Nama minimal 3 karakter'
    }

    if (!email) {
      newErrors.email = 'Email harus diisi'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Format email tidak valid'
    }

    if (!password) {
      newErrors.password = 'Password harus diisi'
    } else if (password.length < 6) {
      newErrors.password = 'Password minimal 6 karakter'
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Konfirmasi password harus diisi'
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Password dan konfirmasi password tidak sama'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      await Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Mohon perbaiki kesalahan pada form',
      })
      return
    }

    try {
      setLoading(true)
      await dispatch(
        registerAdmin({
          name: name.trim(),
          email: email.trim(),
          password,
          confirm_password: confirmPassword,
        })
      ).unwrap()
      await Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Akun admin berhasil dibuat! Anda akan diarahkan ke dashboard.',
        timer: 2000,
        showConfirmButton: false,
      })
      // Navigasi akan di-handle oleh PublicRoute setelah state isAuthenticated berubah
      // Tidak perlu navigate manual untuk menghindari redundansi
    } catch (err: any) {
      await Swal.fire({
        icon: 'error',
        title: 'Registrasi Gagal',
        text: err || 'Gagal membuat akun admin',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-md w-full bg-white rounded-xl shadow-2xl p-8 md:p-10 border border-slate-200">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-2">
            Register Admin
          </h1>
          <p className="text-slate-600">Buat akun admin baru</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Nama Lengkap"
            type="text"
            value={name}
            onChange={(e) => {
              setName(e.target.value)
              if (errors.name) {
                setErrors({ ...errors, name: undefined })
              }
            }}
            placeholder="masukkan nama lengkap"
            required
            error={errors.name}
          />

          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value)
              if (errors.email) {
                setErrors({ ...errors, email: undefined })
              }
            }}
            placeholder="masukkan email"
            required
            error={errors.email}
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              if (errors.password) {
                setErrors({ ...errors, password: undefined })
              }
              // Clear confirm password error jika password berubah
              if (errors.confirmPassword && e.target.value === confirmPassword) {
                setErrors({ ...errors, confirmPassword: undefined })
              }
            }}
            placeholder="masukkan password (min 6 karakter)"
            required
            error={errors.password}
          />

          <Input
            label="Konfirmasi Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value)
              if (errors.confirmPassword) {
                setErrors({ ...errors, confirmPassword: undefined })
              }
            }}
            placeholder="ulangi password"
            required
            error={errors.confirmPassword}
          />

          <Button
            type="submit"
            className="w-full"
            disabled={loading}
          >
            {loading ? 'Memproses...' : 'Daftar Admin'}
          </Button>
        </form>
      </div>
    </div>
  )
}

export default RegisterAdminForm

