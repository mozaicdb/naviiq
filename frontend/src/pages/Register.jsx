import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

function Register() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    age: '',
    school_level: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await axios.post(`${API_URL}/api/auth/register`, {
        ...formData,
        age: parseInt(formData.age),
      })
      navigate('/login?registered=true&email=' + formData.email)
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
      <div className="bg-white w-full max-w-md p-8 rounded-2xl shadow-md">
        
        <h1 className="text-3xl font-bold text-[#0F172A] mb-2">Create your account</h1>
        <p className="text-[#64748B] mb-6">Tell us your age so we can customize your experience.</p>

        {error && (
          <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="text-sm font-medium text-[#0F172A] mb-1 block">Full Name</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              placeholder="Enter your full name"
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]"
            />
          </div>

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
            <label className="text-sm font-medium text-[#0F172A] mb-1 block">Age</label>
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              required
              placeholder="How old are you?"
              min="5"
              max="100"
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-[#0F172A] mb-1 block">School Level</label>
            <select
              name="school_level"
              value={formData.school_level}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB] bg-white"
            >
              <option value="">Select your level</option>
              <option value="secondary">Secondary School</option>
              <option value="university">University Student</option>
              <option value="graduate">Graduate</option>
              <option value="working">Working Professional</option>
              <option value="interested">Just Interested</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-[#0F172A] mb-1 block">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Create a password"
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB] pr-12"
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
              <p className={`text-xs ${formData.password.length >= 8 ? 'text-green-600' : 'text-[#94A3B8]'}`}>
                {formData.password.length >= 8 ? '✓' : '○'} At least 8 characters
              </p>
              <p className={`text-xs ${/[0-9]/.test(formData.password) ? 'text-green-600' : 'text-[#94A3B8]'}`}>
                {/[0-9]/.test(formData.password) ? '✓' : '○'} At least one number
              </p>
              <p className={`text-xs ${/[A-Z]/.test(formData.password) ? 'text-green-600' : 'text-[#94A3B8]'}`}>
                {/[A-Z]/.test(formData.password) ? '✓' : '○'} At least one uppercase letter
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-[#2563EB] text-white font-bold rounded-lg hover:bg-blue-700 transition-all disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-[#64748B] mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-[#2563EB] font-medium hover:underline">
            Login
          </Link>
        </p>

      </div>
    </div>
  )
}

export default Register