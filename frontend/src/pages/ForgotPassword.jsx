import { useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!email) return
    setLoading(true)
    setMessage('')
    setError('')
    try {
      await axios.post(`${API_URL}/api/auth/forgot-password?email=${encodeURIComponent(email)}`)
      setMessage('If this email exists you will receive a reset link.')
    } catch (err) {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-sm p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-[#0F172A] mb-1">Forgot Password</h1>
        <p className="text-sm text-[#64748B] mb-6">Enter your email and we will send you a reset link.</p>

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
          <label className="text-sm font-medium text-[#0F172A] mb-1 block">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB] text-sm"
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading || !email}
          className="w-full py-3 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-blue-700 disabled:opacity-40 transition-all"
        >
          {loading ? 'Sending...' : 'Send Reset Link'}
        </button>

        <p className="text-sm text-center text-[#64748B] mt-4">
          Remember your password?{' '}
          <Link to="/login" className="text-[#2563EB] hover:underline">Login</Link>
        </p>
      </div>
    </div>
  )
}

export default ForgotPassword