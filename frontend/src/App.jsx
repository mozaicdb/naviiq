import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import Landing from './pages/Landing'
import Register from './pages/Register'
import Login from './pages/Login'
import Chat from './pages/Chat'
import Roadmap from './pages/Roadmap'
import VerifyEmail from './pages/VerifyEmail'
import AuthCallback from './pages/AuthCallback'

const API_URL = 'http://localhost:8000'

function ProtectedRoute({ children }) {
  const [checking, setChecking] = useState(true)
  const [authenticated, setAuthenticated] = useState(false)

  useEffect(() => {
    axios.get(`${API_URL}/api/auth/me`, { withCredentials: true })
      .then(() => setAuthenticated(true))
      .catch(() => setAuthenticated(false))
      .finally(() => setChecking(false))
  }, [])

  if (checking) return null

  return authenticated ? children : <Navigate to="/login" replace />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
        <Route path="/roadmap/:shareToken" element={<Roadmap />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App