import { useState } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

function Login() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [formData, setFormData] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const registered = searchParams.get('registered')
  const email = searchParams.get('email')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await axios.post(`${API_URL}/api/auth/login`, formData, {
        withCredentials: true,
      })
      navigate('/chat')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your details.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
      <div className="bg-white w-full max-w-md p-8 rounded-2xl shadow-md">

        <h1 className="text-3xl font-bold text-[#0F172A] mb-2">Welcome back</h1>
        <p className="text-[#64748B] mb-6">Login to continue your journey.</p>

        {registered && (
          <div className="bg-green-50 text-green-700 px-4 py-3 rounded-lg mb-4 text-sm">
            Registration successful! We sent a verification link to {email}. Check your inbox before logging in.
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="text-sm font-medium text-[#0F172A] mb-1 block">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-[#0F172A] mb-1 block">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]"
            />
          </div>

          <div className="text-right">
            <Link to="/forgot-password" className="text-sm text-[#2563EB] hover:underline">
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-[#2563EB] text-white font-bold rounded-lg hover:bg-blue-700 transition-all disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="text-center text-sm text-[#64748B] mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-[#2563EB] font-medium hover:underline">
            Create one
          </Link>
        </p>

      </div>
    </div>
  )
}

export default Login