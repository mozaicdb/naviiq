import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function AuthCallback() {
  const navigate = useNavigate()

  useEffect(() => {
    navigate('/chat', { replace: true })
  }, [])

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
      <p className="text-[#64748B]">Signing you in...</p>
    </div>
  )
}

export default AuthCallback