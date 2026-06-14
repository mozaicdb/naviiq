import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('verifying')

  const hasVerified = useRef(false)

  useEffect(() => {
    if (hasVerified.current) return
    hasVerified.current = true
    const token = searchParams.get('token')
    if (!token) {
      setStatus('invalid')
      return
    }
    verifyToken(token)
  }, [])

  const verifyToken = async (token) => {
    try {
      await axios.get(`${API_URL}/api/auth/verify-email?token=${token}`)
      setStatus('success')
    } catch (err) {
      const message = err.response?.data?.detail || ''
      console.log('Verify error:', message)
      if (message.includes('already verified')) {
        setStatus('already_used')
      } else {
        setStatus('invalid')
      }
    }
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
      <div className="bg-white w-full max-w-md p-8 rounded-2xl shadow-md text-center">

        {status === 'verifying' && (
          <>
            <div className="text-4xl mb-4">⏳</div>
            <h1 className="text-2xl font-bold text-[#0F172A] mb-2">Verifying your email...</h1>
            <p className="text-[#64748B]">Please wait a moment.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="text-4xl mb-4">✅</div>
            <h1 className="text-2xl font-bold text-[#0F172A] mb-2">Email Verified!</h1>
            <p className="text-[#64748B] mb-6">Your account is ready. You can now login.</p>
            <button
              onClick={() => navigate('/login')}
              className="w-full py-3 bg-[#2563EB] text-white font-bold rounded-lg hover:bg-blue-700 transition-all"
            >
              Go to Login
            </button>
          </>
        )}

        {status === 'already_used' && (
          <>
            <div className="text-4xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-[#0F172A] mb-2">Link Already Used</h1>
            <p className="text-[#64748B] mb-6">This verification link has already been used. Please login.</p>
            <button
              onClick={() => navigate('/login')}
              className="w-full py-3 bg-[#2563EB] text-white font-bold rounded-lg hover:bg-blue-700 transition-all"
            >
              Go to Login
            </button>
          </>
        )}

        {status === 'invalid' && (
          <>
            <div className="text-4xl mb-4">❌</div>
            <h1 className="text-2xl font-bold text-[#0F172A] mb-2">Link Expired</h1>
            <p className="text-[#64748B] mb-6">This verification link has expired or is invalid. Please register again.</p>
            <button
              onClick={() => navigate('/register')}
              className="w-full py-3 bg-[#2563EB] text-white font-bold rounded-lg hover:bg-blue-700 transition-all"
            >
              Register Again
            </button>
          </>
        )}

      </div>
    </div>
  )
}

export default VerifyEmail