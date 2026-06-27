import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const NODES = ['Identity', 'Background', 'Strengths', 'Goals', 'Decision', 'Roadmap']

function Chat() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [currentNode, setCurrentNode] = useState(0)
  const [quickReplies, setQuickReplies] = useState([])
  const [nodeToast, setNodeToast] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    startSession()
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startSession = async () => {
    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: 'start' })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let aiText = ''
      let messageAdded = false

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(line => line.startsWith('data: '))

        for (const line of lines) {
          const jsonStr = line.replace('data: ', '')
          try {
            const parsed = JSON.parse(jsonStr)
            if (parsed.token) {
              aiText += parsed.token
              if (!messageAdded) {
                setMessages([{ role: 'ai', text: aiText }])
                messageAdded = true
              } else {
                setMessages([{ role: 'ai', text: aiText }])
              }
            }
            if (parsed.done) {
              setSessionId(parsed.session_id)
              if (parsed.current_stage) updateNode(parsed.current_stage)
            }
          } catch {}
        }
      }
    } catch (err) {
      setMessages([{ role: 'ai', text: 'Something went wrong. Please refresh and try again.' }])
    }
  }

  const updateNode = (stage) => {
    const stageMap = {
      collect_identity: 0,
      identity: 0,
      collect_background: 1,
      background: 1,
      analyze_strengths: 2,
      strengths: 2,
      define_goals: 3,
      goals: 3,
      decision_engine: 4,
      decision: 4,
      roadmap_generator: 5,
      roadmap: 5,
      completed: 5,
    }
    const index = stageMap[stage]
    if (index !== undefined && index !== currentNode) {
      setCurrentNode(index)
      showNodeToast(index)
    }
  }

  const showNodeToast = (index) => {
    const toasts = [
      'Getting to know you...',
      'Understanding your background...',
      'Analyzing your strengths...',
      'Mapping your goals...',
      'Finding your best career path...',
      'Generating your roadmap...',
    ]
    setNodeToast(toasts[index])
    setTimeout(() => setNodeToast(''), 3000)
  }

  const sendMessage = async (text) => {
    const userText = text || input.trim()
    if (!userText) return

    setMessages((prev) => [...prev, { role: 'user', text: userText }])
    setInput('')
    setQuickReplies([])
    setLoading(true)

    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: userText, session_id: sessionId })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let aiText = ''
      let messageAdded = false

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(line => line.startsWith('data: '))

        for (const line of lines) {
          const jsonStr = line.replace('data: ', '')
          try {
            const parsed = JSON.parse(jsonStr)
            if (parsed.token) {
              aiText += parsed.token
              const currentText = aiText
              if (!messageAdded) {
                setMessages((prev) => [...prev, { role: 'ai', text: currentText }])
                messageAdded = true
              } else {
                setMessages((prev) => {
                  const updated = [...prev]
                  updated[updated.length - 1] = { role: 'ai', text: currentText }
                  return updated
                })
              }
              await new Promise(resolve => setTimeout(resolve, 20))
            }
            if (parsed.done) {
              if (parsed.current_stage) updateNode(parsed.current_stage)
              if (parsed.roadmap_complete) {
                setTimeout(() => navigate(`/roadmap/${parsed.share_token}`), 1500)
              }
            }
          } catch {}
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'ai', text: 'Something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col">

      {/* Header */}
      <header className="bg-white shadow-sm px-4 py-3 flex flex-col gap-2 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-[#2563EB]">Naviiq</h1>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            <span className="text-sm text-[#64748B]">Online</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="flex items-center gap-1">
          {NODES.map((node, i) => (
            <div key={node} className="flex-1 flex flex-col items-center gap-1">
              <div
                className={`h-1.5 w-full rounded-full transition-all ${
                  i <= currentNode ? 'bg-[#2563EB]' : 'bg-gray-200'
                }`}
              />
              <span className={`text-xs hidden md:block ${i <= currentNode ? 'text-[#2563EB] font-medium' : 'text-gray-400'}`}>
                {node}
              </span>
            </div>
          ))}
        </div>
      </header>

      {/* Node Toast */}
      {nodeToast && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 bg-[#0F172A] text-white text-sm px-4 py-2 rounded-full shadow-lg z-20">
          🧠 {nodeToast}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'ai' && (
              <div className="w-8 h-8 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-sm font-bold mr-2 mt-1 shrink-0">
                N
              </div>
            )}
            <div
              className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-[#2563EB] text-white rounded-tr-sm'
                  : 'bg-white text-[#0F172A] shadow-sm rounded-tl-sm'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="w-8 h-8 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-sm font-bold mr-2 shrink-0">
              N
            </div>
            <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm flex gap-1 items-center">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]"></span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Quick Replies */}
      {quickReplies.length > 0 && (
        <div className="px-4 pb-2 flex gap-2 flex-wrap">
          {quickReplies.map((reply, i) => (
            <button
              key={i}
              onClick={() => sendMessage(reply)}
              className="px-4 py-2 bg-white border border-[#2563EB] text-[#2563EB] text-sm rounded-full hover:bg-blue-50 transition-all"
            >
              {reply}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-100 px-4 py-3 flex gap-3 items-end">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          rows={1}
          className="flex-1 resize-none px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB] text-sm max-h-32"
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="px-5 py-3 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-blue-700 disabled:opacity-40 transition-all"
        >
          Send
        </button>
      </div>

    </div>
  )
}

export default Chat