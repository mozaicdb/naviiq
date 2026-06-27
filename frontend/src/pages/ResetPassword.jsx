import { useState } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { Eye, EyeOff } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const handleSubmit = async () => {
    setError('')
    setMessage('')

    if (!newPassword || !confirmPassword) {
      setError('Please fill in both fields.')
      return
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    if (newPassword.length < 8 || !/[0-9]/.test(newPassword) || !/[A-Z]/.test(newPassword)) {
      setError('Password must be at least 8 characters, with one number and one uppercase letter.')
      return
    }
    if (!token) {
      setError('Reset token is missing or invalid.')
      return
    }

    setLoading(true)
    try {
      await axios.post(
        `${API_URL}/api/auth/reset-password?token=${encodeURIComponent(token)}&new_password=${encodeURIComponent(newPassword)}`
      )
      setMessage('Password reset successful. Redirecting to login...')
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      setError('This reset link is invalid or has expired.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-sm p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-[#0F172A] mb-1">Reset Password</h1>
        <p className="text-sm text-[#64748B] mb-6">Enter your new password below.</p>

        {message && (
          <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl text-sm">
            {message}
          </div>
        )}

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm">
            {error}
          </div>
        )}

        <div className="mb-4">
          <label className="text-sm font-medium text-[#0F172A] mb-1 block">New Password</label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter new password"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB] text-sm pr-12"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#64748B]"
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          <div className="mt-2 flex flex-col gap-1">
            <p className={`text-xs ${newPassword.length >= 8 ? 'text-green-600' : 'text-[#94A3B8]'}`}>
              {newPassword.length >= 8 ? '✓' : '○'} At least 8 characters
            </p>
            <p className={`text-xs ${/[0-9]/.test(newPassword) ? 'text-green-600' : 'text-[#94A3B8]'}`}>
              {/[0-9]/.test(newPassword) ? '✓' : '○'} At least one number
            </p>
            <p className={`text-xs ${/[A-Z]/.test(newPassword) ? 'text-green-600' : 'text-[#94A3B8]'}`}>
              {/[A-Z]/.test(newPassword) ? '✓' : '○'} At least one uppercase letter
            </p>
          </div>
        </div>

        <div className="mb-4">
          <label className="text-sm font-medium text-[#0F172A] mb-1 block">Confirm Password</label>
          <input
            type={showPassword ? 'text' : 'password'}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB] text-sm"
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full py-3 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-blue-700 disabled:opacity-40 transition-all"
        >
          {loading ? 'Resetting...' : 'Reset Password'}
        </button>

        <p className="text-sm text-center text-[#64748B] mt-4">
          Remember your password?{' '}
          <Link to="/login" className="text-[#2563EB] hover:underline">Login</Link>
        </p>
      </div>
    </div>
  )
}

export default ResetPassword