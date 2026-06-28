import { useState, useEffect, useRef } from 'react'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { useParams } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function parseRoadmap(text) {
  const sections = {}
  const sectionHeaders = [
    'WHY THIS PATH FITS YOU',
    'JOB ROLES YOU CAN GROW INTO',
    'SKILLS TO LEARN IN ORDER',
    'YOUR LEARNING PLAN',
    'RECOMMENDED FREE COURSES',
    'FIRST PROJECT TO BUILD',
    'CLOSING MESSAGE'
  ]

  let current = null
  const lines = text.split('\n')

  for (const line of lines) {
    const trimmed = line.trim()
    const matched = sectionHeaders.find(h => trimmed.replace(/^##\s*/, '').toUpperCase() === h)
    if (matched) {
      current = matched
      sections[current] = []
    } else if (current && trimmed) {
      sections[current].push(trimmed)
    }
  }

  return sections
}

function extractLinks(text) {
  const urlRegex = /(https?:\/\/[^\s]+)/g
  const parts = []
  let last = 0
  let match

  while ((match = urlRegex.exec(text)) !== null) {
    if (match.index > last) parts.push({ type: 'text', value: text.slice(last, match.index) })
    parts.push({ type: 'link', value: match[0] })
    last = match.index + match[0].length
  }

  if (last < text.length) parts.push({ type: 'text', value: text.slice(last) })
  return parts
}

function TextWithLinks({ text }) {
  const parts = extractLinks(text)
  return (
    <span>
      {parts.map((part, i) =>
        part.type === 'link' ? (
          <a key={i} href={part.value} target="_blank" rel="noopener noreferrer"
            className="text-[#2563EB] underline break-all font-medium hover:text-blue-800">
            {part.value}
          </a>
        ) : (
          <span key={i}>{part.value}</span>
        )
      )}
    </span>
  )
}

function Section({ title, color, children }) {
  return (
    <div className={`bg-white rounded-2xl shadow-sm overflow-hidden mb-4`}>
      <div className={`px-6 py-3 ${color}`}>
        <h3 className="text-white font-bold text-sm uppercase tracking-wider">{title}</h3>
      </div>
      <div className="px-6 py-5">
        {children}
      </div>
    </div>
  )
}

function Roadmap() {
  const { shareToken } = useParams()
  const [roadmap, setRoadmap] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const roadmapRef = useRef(null)

  useEffect(() => {
    fetchRoadmap()
  }, [shareToken])

  const fetchRoadmap = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/chat/roadmap/${shareToken}`)
      setRoadmap(res.data)
    } catch (err) {
      setError('Roadmap not found or link is invalid.')
    } finally {
      setLoading(false)
    }
  }

  const downloadPDF = async () => {
    const element = roadmapRef.current
    const canvas = await html2canvas(element, { scale: 2 })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width
    pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)
    pdf.save('naviiq-roadmap.pdf')
  }

  const copyLink = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <p className="text-[#64748B]">Loading your roadmap...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    )
  }

  const sections = parseRoadmap(roadmap.roadmap_response || '')

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-32">

      <div ref={roadmapRef}>
        {/* Header */}
        <header className="bg-white shadow-sm px-6 py-4 flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-[#2563EB] text-white flex items-center justify-center font-bold text-sm">N</div>
          <h1 className="text-xl font-bold text-[#2563EB]">Naviiq</h1>
        </header>

        {/* Hero */}
        <section className="bg-[#2563EB] text-white px-6 py-10 text-center">
          <p className="text-xs uppercase tracking-widest mb-2 text-blue-200">Your Personalized Career Roadmap</p>
          <h2 className="text-2xl font-bold mb-1">{roadmap.matched_category}</h2>
          {roadmap.confidence_score && (
            <div className="mt-3 inline-block bg-white text-[#2563EB] px-4 py-1.5 rounded-full font-bold text-sm">
              {roadmap.confidence_score}% Match Confidence
            </div>
          )}
        </section>

        {/* Sections */}
        <div className="max-w-2xl mx-auto px-4 py-6">

          {sections['WHY THIS PATH FITS YOU'] && (
            <Section title="Why This Path Fits You" color="bg-[#2563EB]">
              <p className="text-[#0F172A] leading-relaxed text-sm">
                <TextWithLinks text={sections['WHY THIS PATH FITS YOU'].join(' ')} />
              </p>
            </Section>
          )}

          {sections['JOB ROLES YOU CAN GROW INTO'] && (
            <Section title="Job Roles You Can Grow Into" color="bg-[#0F172A]">
              <div className="flex flex-col gap-3">
                {sections['JOB ROLES YOU CAN GROW INTO'].map((line, i) => (
                  <div key={i} className="bg-[#F8FAFC] rounded-xl px-4 py-3 text-sm text-[#0F172A]">
                    <TextWithLinks text={line} />
                  </div>
                ))}
              </div>
            </Section>
          )}

          {sections['SKILLS TO LEARN IN ORDER'] && (
            <Section title="Skills to Learn in Order" color="bg-[#14B8A6]">
              <div className="flex flex-col gap-2">
                {sections['SKILLS TO LEARN IN ORDER'].map((line, i) => (
                  <div key={i} className="flex gap-3 items-start">
                    <div className="w-6 h-6 rounded-full bg-[#14B8A6] text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                      {i + 1}
                    </div>
                    <p className="text-sm text-[#0F172A]"><TextWithLinks text={line} /></p>
                  </div>
                ))}
              </div>
            </Section>
          )}

          {sections['YOUR LEARNING PLAN'] && (
            <Section title="Your Learning Plan" color="bg-[#F59E0B]">
              <div className="flex flex-col gap-2">
                {sections['YOUR LEARNING PLAN'].map((line, i) => (
                  <div key={i} className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-[#F59E0B] shrink-0 mt-2"></div>
                    <p className="text-sm text-[#0F172A]"><TextWithLinks text={line} /></p>
                  </div>
                ))}
              </div>
            </Section>
          )}

          {sections['RECOMMENDED FREE COURSES'] && (
            <Section title="Recommended Free Courses" color="bg-[#7C3AED]">
              <div className="flex flex-col gap-3">
                {sections['RECOMMENDED FREE COURSES'].map((line, i) => {
                  const urlMatch = line.match(/(https?:\/\/[^\s]+)/)
                  const url = urlMatch ? urlMatch[0] : null
                  const text = line.replace(/(https?:\/\/[^\s]+)/, '').trim()
                  return (
                    <div key={i} className="bg-[#F8FAFC] rounded-xl px-4 py-3">
                      <p className="text-sm text-[#0F172A] mb-2">{text}</p>
                      {url && (
                        <a href={url} target="_blank" rel="noopener noreferrer"
                          className="inline-block bg-[#7C3AED] text-white text-xs px-3 py-1.5 rounded-full font-medium hover:bg-purple-700 transition-all">
                          Open Course
                        </a>
                      )}
                    </div>
                  )
                })}
              </div>
            </Section>
          )}

          {sections['FIRST PROJECT TO BUILD'] && (
            <Section title="First Project to Build" color="bg-[#DC2626]">
              <div className="flex flex-col gap-2">
                {sections['FIRST PROJECT TO BUILD'].map((line, i) => (
                  <div key={i} className="bg-[#F8FAFC] rounded-xl px-4 py-3 text-sm text-[#0F172A]">
                    <TextWithLinks text={line} />
                  </div>
                ))}
              </div>
            </Section>
          )}

          {sections['CLOSING MESSAGE'] && (
            <div className="bg-[#2563EB] rounded-2xl px-6 py-6 text-center text-white mt-4">
              <p className="text-sm leading-relaxed">
                {sections['CLOSING MESSAGE'].join(' ')}
              </p>
            </div>
          )}

          {roadmap.infrastructure_adjusted && (
            <div className="mt-4 bg-amber-50 border border-amber-200 px-4 py-3 rounded-xl text-sm text-amber-800">
              This roadmap has been adjusted for low data and power constraints.
            </div>
          )}

        </div>
      </div>

      {/* Action Buttons */}
      <div className="fixed bottom-6 left-0 right-0 px-4 flex flex-col gap-2 max-w-2xl mx-auto">
        <button onClick={downloadPDF}
          className="w-full py-4 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-blue-700 transition-all">
          Download PDF
        </button>
        <button onClick={copyLink}
          className="w-full py-4 bg-[#F59E0B] text-white font-bold rounded-xl hover:bg-amber-500 transition-all">
          {copied ? 'Link Copied!' : 'Share This Roadmap'}
        </button>
      </div>

    </div>
  )
}

export default Roadmap