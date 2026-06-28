import { useState, useEffect } from 'react'
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

function extractUrls(text) {
  const urlRegex = /(https?:\/\/[^\s]+)/g
  return text.match(urlRegex) || []
}

function stripUrls(text) {
  return text.replace(/(https?:\/\/[^\s]+)/g, '').trim()
}

function generatePrintHTML(roadmap, sections) {
  const date = new Date().toLocaleDateString('en-GB', { year: 'numeric', month: 'long', day: 'numeric' })

  const sectionHTML = (title, bgColor, content) => `
    <div class="section">
      <div class="section-header" style="background:${bgColor}">${title}</div>
      <div class="section-body">${content}</div>
    </div>
  `

  const whyContent = (sections['WHY THIS PATH FITS YOU'] || []).join(' ')

  const jobContent = (sections['JOB ROLES YOU CAN GROW INTO'] || []).map(line => `
    <div class="card">
      <p>${line}</p>
    </div>
  `).join('')

  const skillsContent = (sections['SKILLS TO LEARN IN ORDER'] || []).map((line, i) => {
    const clean = line.replace(/^\d+\.\s*/, '')
    return `
      <div class="skill-item">
        <div class="skill-num">${i + 1}</div>
        <p>${clean}</p>
      </div>
    `
  }).join('')

  const planContent = (sections['YOUR LEARNING PLAN'] || []).map(line => `
    <div class="plan-item">
      <div class="dot"></div>
      <p>${line}</p>
    </div>
  `).join('')

  const courseContent = (sections['RECOMMENDED FREE COURSES'] || []).map(line => {
    const urls = extractUrls(line)
    const text = stripUrls(line)
    const url = urls[0] || ''
    return `
      <div class="card">
        <p>${text}</p>
        ${url ? `<a href="${url}" class="course-link">${url}</a>` : ''}
      </div>
    `
  }).join('')

  const projectContent = (sections['FIRST PROJECT TO BUILD'] || []).map(line => `
    <div class="card">
      <p>${line}</p>
    </div>
  `).join('')

  const closingContent = (sections['CLOSING MESSAGE'] || []).join(' ')

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Naviiq Career Roadmap</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #fff; color: #0F172A; font-size: 13px; line-height: 1.6; }
        
        .header { background: #2563EB; color: white; padding: 24px 32px; display: flex; align-items: center; justify-content: space-between; }
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo-circle { width: 36px; height: 36px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #2563EB; font-weight: 900; font-size: 16px; }
        .logo-text { font-size: 22px; font-weight: 800; color: white; }
        .header-right { text-align: right; }
        .header-right p { font-size: 11px; color: rgba(255,255,255,0.8); }
        .header-right .confidence { background: white; color: #2563EB; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 12px; display: inline-block; margin-top: 6px; }

        .hero { background: #1E40AF; color: white; padding: 20px 32px; }
        .hero p { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: rgba(255,255,255,0.7); margin-bottom: 4px; }
        .hero h1 { font-size: 24px; font-weight: 800; }

        .content { padding: 24px 32px; }

        .section { margin-bottom: 20px; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
        .section-header { padding: 10px 16px; color: white; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
        .section-body { padding: 16px; background: white; }

        .card { background: #F8FAFC; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px; }
        .card:last-child { margin-bottom: 0; }
        .card p { font-size: 12px; color: #0F172A; line-height: 1.6; }

        .skill-item { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 10px; }
        .skill-num { width: 24px; height: 24px; border-radius: 50%; background: #14B8A6; color: white; font-weight: 700; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; }
        .skill-item p { font-size: 12px; color: #0F172A; line-height: 1.6; }

        .plan-item { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px; }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: #F59E0B; flex-shrink: 0; margin-top: 5px; }
        .plan-item p { font-size: 12px; color: #0F172A; }

        .course-link { display: inline-block; margin-top: 6px; color: #2563EB; font-size: 11px; word-break: break-all; text-decoration: underline; }

        .closing { background: #2563EB; color: white; padding: 20px 24px; border-radius: 10px; text-align: center; font-size: 13px; line-height: 1.7; margin-bottom: 20px; }

        .footer { border-top: 1px solid #E2E8F0; padding: 16px 32px; display: flex; justify-content: space-between; color: #94A3B8; font-size: 10px; }

        .watermark {
          position: fixed;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%) rotate(-45deg);
          font-size: 80px;
          font-weight: 900;
          color: rgba(37, 99, 235, 0.06);
          white-space: nowrap;
          pointer-events: none;
          z-index: 0;
          letter-spacing: 8px;
        }
        @media print {
          body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
          .no-print { display: none; }
          @page { margin: 0; size: A4; }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <div class="logo">
          <div class="logo-circle">N</div>
          <span class="logo-text">Naviiq</span>
        </div>
        <div class="header-right">
          <p>Your Personalized Career Roadmap</p>
          ${roadmap.confidence_score ? `<span class="confidence">${roadmap.confidence_score}% Match Confidence</span>` : ''}
        </div>
      </div>

      <div class="hero">
        <p>Career Path</p>
        <h1>${roadmap.matched_category || ''}</h1>
      </div>

      <div class="content">
        ${whyContent ? sectionHTML('Why This Path Fits You', '#2563EB', `<p>${whyContent}</p>`) : ''}
        ${jobContent ? sectionHTML('Job Roles You Can Grow Into', '#0F172A', jobContent) : ''}
        ${skillsContent ? sectionHTML('Skills to Learn in Order', '#14B8A6', skillsContent) : ''}
        ${planContent ? sectionHTML('Your Learning Plan', '#F59E0B', planContent) : ''}
        ${courseContent ? sectionHTML('Recommended Free Courses', '#7C3AED', courseContent) : ''}
        ${projectContent ? sectionHTML('First Project to Build', '#DC2626', projectContent) : ''}
        ${closingContent ? `<div class="closing">${closingContent}</div>` : ''}
      </div>

      <div class="watermark">MOZAICTECK</div>
      <div class="footer">
        <span>Generated by Naviiq</span>
        <span>${date}</span>
      </div>
    </body>
    </html>
  `
}

function TextWithLinks({ text }) {
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

  return (
    <span>
      {parts.map((part, i) =>
        part.type === 'link' ? (
          <a key={i} href={part.value} target="_blank" rel="noopener noreferrer"
            className="text-[#2563EB] underline break-all font-medium hover:text-blue-800">
            {part.value}
          </a>
        ) : <span key={i}>{part.value}</span>
      )}
    </span>
  )
}

function Section({ title, color, children }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm overflow-hidden mb-4">
      <div className="px-6 py-3" style={{ background: color }}>
        <h3 className="text-white font-bold text-xs uppercase tracking-wider">{title}</h3>
      </div>
      <div className="px-6 py-5">{children}</div>
    </div>
  )
}

function Roadmap() {
  const { shareToken } = useParams()
  const [roadmap, setRoadmap] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

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

  const downloadPDF = () => {
    const sections = parseRoadmap(roadmap.roadmap_response || '')
    const html = generatePrintHTML(roadmap, sections)
    const printWindow = window.open('', '_blank')
    printWindow.document.write(html)
    printWindow.document.close()
    printWindow.focus()
    setTimeout(() => {
      printWindow.print()
    }, 500)
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

      <header className="bg-white shadow-sm px-6 py-4 flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-[#2563EB] text-white flex items-center justify-center font-bold text-sm">N</div>
        <h1 className="text-xl font-bold text-[#2563EB]">Naviiq</h1>
      </header>

      <section className="bg-[#2563EB] text-white px-6 py-10 text-center">
        <p className="text-xs uppercase tracking-widest mb-2 text-blue-200">Your Personalized Career Roadmap</p>
        <h2 className="text-2xl font-bold mb-1">{roadmap.matched_category}</h2>
        {roadmap.confidence_score && (
          <div className="mt-3 inline-block bg-white text-[#2563EB] px-4 py-1.5 rounded-full font-bold text-sm">
            {roadmap.confidence_score}% Match Confidence
          </div>
        )}
      </section>

      <div className="max-w-2xl mx-auto px-4 py-6">

        {sections['WHY THIS PATH FITS YOU'] && (
          <Section title="Why This Path Fits You" color="#2563EB">
            <p className="text-[#0F172A] leading-relaxed text-sm">
              <TextWithLinks text={sections['WHY THIS PATH FITS YOU'].join(' ')} />
            </p>
          </Section>
        )}

        {sections['JOB ROLES YOU CAN GROW INTO'] && (
          <Section title="Job Roles You Can Grow Into" color="#0F172A">
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
          <Section title="Skills to Learn in Order" color="#14B8A6">
            <div className="flex flex-col gap-3">
              {sections['SKILLS TO LEARN IN ORDER'].map((line, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div className="w-6 h-6 rounded-full bg-[#14B8A6] text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                    {i + 1}
                  </div>
                  <p className="text-sm text-[#0F172A]"><TextWithLinks text={line.replace(/^\d+\.\s*/, '')} /></p>
                </div>
              ))}
            </div>
          </Section>
        )}

        {sections['YOUR LEARNING PLAN'] && (
          <Section title="Your Learning Plan" color="#F59E0B">
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
          <Section title="Recommended Free Courses" color="#7C3AED">
            <div className="flex flex-col gap-3">
              {sections['RECOMMENDED FREE COURSES'].map((line, i) => {
                const urls = extractUrls(line)
                const url = urls[0] || null
                const text = stripUrls(line)
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
          <Section title="First Project to Build" color="#DC2626">
            <div className="flex flex-col gap-3">
              {sections['FIRST PROJECT TO BUILD'].map((line, i) => (
                <div key={i} className="bg-[#F8FAFC] rounded-xl px-4 py-3 text-sm text-[#0F172A]">
                  <TextWithLinks text={line} />
                </div>
              ))}
            </div>
          </Section>
        )}

        {sections['CLOSING MESSAGE'] && (
          <div className="bg-[#2563EB] rounded-2xl px-6 py-6 text-center text-white mt-2 mb-4">
            <p className="text-sm leading-relaxed">{sections['CLOSING MESSAGE'].join(' ')}</p>
          </div>
        )}

        {roadmap.infrastructure_adjusted && (
          <div className="mt-4 bg-amber-50 border border-amber-200 px-4 py-3 rounded-xl text-sm text-amber-800">
            This roadmap has been adjusted for low data and power constraints.
          </div>
        )}

      </div>

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