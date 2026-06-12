import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Register from './pages/Register'
import Login from './pages/Login'
import Chat from './pages/Chat'
import Roadmap from './pages/Roadmap'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/roadmap/:shareToken" element={<Roadmap />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App