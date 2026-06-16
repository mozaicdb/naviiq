import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

function AuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  useEffect(() => {
    const accessToken = searchParams.get('access_token')
    const refreshToken = searchParams.get('refresh_token')

    if (accessToken && refreshToken) {
      document.cookie = `access_token=${accessToken}; path=/; max-age=900; samesite=lax`
      document.cookie = `refresh_token=${refreshToken}; path=/; max-age=604800; samesite=lax`
      navigate('/chat', { replace: true })
    } else {
      navigate('/login', { replace: true })
    }
  }, [])

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
      <p className="text-[#64748B]">Signing you in...</p>
    </div>
  )
}

export default AuthCallback