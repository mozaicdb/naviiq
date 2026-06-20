import { useState, useEffect, useRef } from 'react'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'

const API_URL = 'http://localhost:8000'

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

  const roadmapRef = useRef(null)

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

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-24">

      {/* Header */}
      <header className="bg-white shadow-sm px-6 py-4">
        <h1 className="text-2xl font-bold text-[#2563EB]">Naviiq</h1>
      </header>

      {/* Hero */}
      <section className="bg-[#2563EB] text-white px-6 py-12 text-center">
        <p className="text-sm uppercase tracking-widest mb-2 text-blue-200">Your Personalized Roadmap</p>
        <h2 className="text-3xl font-bold mb-2">{roadmap.matched_category}</h2>
        <p className="text-blue-200 text-sm">Mode: {roadmap.student_mode}</p>
        {roadmap.confidence_score && (
          <div className="mt-4 inline-block bg-white text-[#2563EB] px-4 py-2 rounded-full font-bold text-sm">
            {roadmap.confidence_score}% Match Confidence
          </div>
        )}
      </section>

      {/* Roadmap Content */}
      <section ref={roadmapRef} className="max-w-2xl mx-auto px-6 py-10">
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h3 className="text-lg font-bold text-[#0F172A] mb-4">Your Guidance</h3>
          <div className="text-[#0F172A] leading-relaxed prose max-w-none">
            <ReactMarkdown>
              {roadmap.roadmap_response}
            </ReactMarkdown>
          </div>
        </div>

        {roadmap.infrastructure_adjusted && (
          <div className="mt-4 bg-amber-50 border border-amber-200 px-4 py-3 rounded-xl text-sm text-amber-800">
            This roadmap has been adjusted for low data and power constraints.
          </div>
        )}
      </section>

      {/* Share Button */}
      <div className="fixed bottom-6 left-0 right-0 px-6 flex flex-col gap-2 max-w-2xl mx-auto">
        <button
          onClick={downloadPDF}
          className="w-full py-4 bg-[#2563EB] text-white font-bold rounded-xl text-center hover:bg-blue-700 transition-all"
        >
          Download PDF
        </button>
        <button
          onClick={copyLink}
          className="w-full max-w-2xl mx-auto block py-4 bg-[#F59E0B] text-white font-bold rounded-xl text-center hover:bg-amber-500 transition-all"
        >
          {copied ? 'Link Copied!' : 'Share This Roadmap'}
        </button>
      </div>

    </div>
  )
}

export default Roadmap