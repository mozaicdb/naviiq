import { useNavigate } from 'react-router-dom'
import { Code2, Palette, BarChart3, Settings, HelpCircle } from 'lucide-react'
import { motion, useInView, animate } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'

function AnimatedCounter({ value, inView }) {
  const [display, setDisplay] = useState(0)
  useEffect(() => {
    if (!inView) return
    const controls = animate(0, value, {
      duration: 1.4,
      onUpdate: (v) => setDisplay(Math.round(v)),
    })
    return () => controls.stop()
  }, [inView, value])
  return <>{display}%</>
}

function AIJourneySection({ navigate }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.3 })
  const stages = ['Identity', 'Background', 'Strengths', 'Goals', 'Decision', 'Roadmap']

  return (
    <section
      ref={ref}
      className="relative px-6 py-20 bg-gradient-to-b from-white to-[#F8FAFC] overflow-hidden"
    >
      <style>{`
        @keyframes floatSlow {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-8px) rotate(3deg); }
        }
        @keyframes floatSlowReverse {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(8px) rotate(-3deg); }
        }
        @keyframes glowPulse {
          0%, 100% { box-shadow: 0 0 0px rgba(37,99,235,0.0); }
          50% { box-shadow: 0 0 24px rgba(37,99,235,0.35); }
        }
        .float-icon-a { animation: floatSlow 4s ease-in-out infinite; }
        .float-icon-b { animation: floatSlowReverse 4.5s ease-in-out infinite; }
        .glow-card { animation: glowPulse 2.6s ease-in-out infinite; }
      `}</style>

      <motion.h2
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
        className="text-3xl font-bold text-center text-[#0F172A] mb-2"
      >
        From Confused to Confident
      </motion.h2>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="text-center text-[#64748B] mb-14 max-w-lg mx-auto"
      >
        Naviiq doesn't guess your career. It evaluates multiple paths, scores each one, and shows you the strongest fit.
      </motion.p>

      <div className="max-w-5xl mx-auto relative">

        <svg
          className="hidden md:block absolute top-24 left-0 w-full h-2 pointer-events-none"
          viewBox="0 0 800 10"
          preserveAspectRatio="none"
        >
          <motion.line
            x1="120" y1="5" x2="380" y2="5"
            stroke="#94A3B8" strokeWidth="2" strokeDasharray="6 6"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={isInView ? { pathLength: 1, opacity: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.5 }}
          />
          <motion.line
            x1="420" y1="5" x2="680" y2="5"
            stroke="#2563EB" strokeWidth="2"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={isInView ? { pathLength: 1, opacity: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.9 }}
          />
        </svg>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 items-start relative z-10">

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <p className="text-xs font-bold text-[#94A3B8] uppercase tracking-wider mb-4 text-center">Before Naviiq</p>
            <div className="relative h-48 flex items-center justify-center">
              <div className="float-icon-a absolute top-2 left-4 opacity-40">
                <Code2 size={26} className="text-[#2563EB]" />
              </div>
              <div className="float-icon-b absolute top-4 right-6 opacity-35">
                <Palette size={26} className="text-[#F59E0B]" />
              </div>
              <div className="float-icon-a absolute bottom-8 left-2 opacity-35">
                <BarChart3 size={26} className="text-[#14B8A6]" />
              </div>
              <div className="float-icon-b absolute bottom-4 right-2 opacity-40">
                <Settings size={26} className="text-[#64748B]" />
              </div>
              <div className="float-icon-a absolute top-0 right-1/3 text-xl text-[#94A3B8] opacity-60 font-bold">?</div>
              <div className="float-icon-b absolute bottom-0 left-1/3 text-xl text-[#94A3B8] opacity-50 font-bold">?</div>

              <motion.div
                animate={isInView ? { scale: [1, 1.08, 1] } : {}}
                transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                className="w-20 h-20 rounded-full bg-white border-2 border-[#E2E8F0] flex items-center justify-center shadow-sm relative z-10"
              >
                <HelpCircle size={36} className="text-[#94A3B8]" />
              </motion.div>
            </div>
            <p className="text-center text-sm text-[#64748B] mt-2">
              "I don't know which tech career fits me."
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.35 }}
          >
            <p className="text-xs font-bold text-[#2563EB] uppercase tracking-wider mb-4 text-center">Naviiq AI Engine</p>
            <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm">
              <div className="space-y-2 mb-4">
                {stages.map((stage, i) => (
                  <motion.div
                    key={stage}
                    className="flex items-center gap-2"
                    initial={{ opacity: 0, x: -10 }}
                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.4, delay: 0.5 + i * 0.15 }}
                  >
                    <motion.div
                      className="w-2 h-2 rounded-full bg-[#2563EB]"
                      animate={isInView ? { scale: [1, 1.6, 1] } : {}}
                      transition={{ duration: 0.5, delay: 0.5 + i * 0.15 }}
                    />
                    <span className="text-xs text-[#64748B]">{stage}</span>
                  </motion.div>
                ))}
              </div>
              <div className="flex justify-center gap-3 pt-2 border-t border-[#F1F5F9]">
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={isInView ? { opacity: 0.5, scale: 1 } : {}}
                  transition={{ duration: 0.5, delay: 1.5 }}
                  className="text-center px-2 py-2 rounded-lg bg-[#F8FAFC] text-xs"
                >
                  <p className="font-semibold text-[#0F172A]">Data</p>
                  <p className="text-[#64748B]">74%</p>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={isInView ? { opacity: 1, scale: 1 } : {}}
                  transition={{ duration: 0.5, delay: 1.7 }}
                  className="text-center px-3 py-2 rounded-lg bg-[#EFF6FF] border border-[#2563EB] glow-card text-xs"
                >
                  <p className="font-bold text-[#2563EB]">Software Eng</p>
                  <p className="text-[#2563EB] font-semibold">
                    <AnimatedCounter value={92} inView={isInView} />
                  </p>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={isInView ? { opacity: 0.5, scale: 1 } : {}}
                  transition={{ duration: 0.5, delay: 1.5 }}
                  className="text-center px-2 py-2 rounded-lg bg-[#F8FAFC] text-xs"
                >
                  <p className="font-semibold text-[#0F172A]">Design</p>
                  <p className="text-[#64748B]">68%</p>
                </motion.div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <p className="text-xs font-bold text-[#10B981] uppercase tracking-wider mb-4 text-center">After Naviiq</p>
            <motion.div
              initial={{ scale: 0.95 }}
              animate={isInView ? { scale: 1 } : {}}
              transition={{ duration: 0.5, delay: 2 }}
              className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-md text-center"
            >
              <p className="text-xs text-[#64748B] mb-1">Best Match</p>
              <h3 className="text-lg font-bold text-[#0F172A] mb-1">Software Engineer</h3>
              <p className="text-2xl font-bold text-[#2563EB] mb-3">
                <AnimatedCounter value={92} inView={isInView} />
              </p>
              <p className="text-xs text-[#64748B] mb-4">Starts with: Python Fundamentals</p>
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate('/register')}
                className="w-full px-4 py-3 bg-[#F59E0B] text-white font-bold rounded-xl hover:bg-amber-500 transition-all text-sm"
              >
                Start Your Journey
              </motion.button>
            </motion.div>
          </motion.div>

        </div>
      </div>
    </section>
  )
}

function Landing() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col">
      
      {/* Navbar */}
      <nav className="flex items-center justify-between px-6 py-4 bg-white shadow-sm">
        <h1 className="text-2xl font-bold text-[#2563EB]">Naviiq</h1>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 text-[#2563EB] font-medium hover:underline"
          >
            Login
          </button>
          <button
            onClick={() => navigate('/register')}
            className="px-4 py-2 bg-[#2563EB] text-white font-medium rounded-lg hover:bg-blue-700"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-20 flex-1">
        <h1 className="text-4xl md:text-6xl font-extrabold text-[#0F172A] leading-tight max-w-3xl">
          Find Your Tech Career.<br />
          <span className="text-[#2563EB]">Without the Guesswork.</span>
        </h1>
        <p className="mt-6 text-lg text-[#64748B] max-w-xl">
          Chat with Naviiq, discover your strengths, and get a personalized learning roadmap in minutes.
        </p>
        <button
          onClick={() => navigate('/register')}
          className="mt-8 px-8 py-4 bg-[#F59E0B] text-white text-lg font-bold rounded-xl hover:bg-amber-500 transition-all"
        >
          Start Your Journey
        </button>
      </section>

      {/* AI Decision Journey Section */}
      <AIJourneySection navigate={navigate} />

      {/* How It Works */}
      <section className="bg-white px-6 py-16">
        <h2 className="text-3xl font-bold text-center text-[#0F172A] mb-12">How It Works</h2>
        <div className="flex flex-col md:flex-row gap-8 max-w-4xl mx-auto">
          {[
            { step: '1', title: 'Chat', desc: 'Answer a few simple questions about yourself.' },
            { step: '2', title: 'Discover', desc: 'Naviiq analyzes your strengths and goals.' },
            { step: '3', title: 'Get Your Roadmap', desc: 'Receive a personalized learning plan built for you.' },
          ].map((item) => (
            <div key={item.step} className="flex-1 text-center p-6 rounded-2xl border border-gray-100 shadow-sm">
              <div className="w-12 h-12 bg-[#2563EB] text-white text-xl font-bold rounded-full flex items-center justify-center mx-auto mb-4">
                {item.step}
              </div>
              <h3 className="text-xl font-semibold text-[#0F172A] mb-2">{item.title}</h3>
              <p className="text-[#64748B]">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Three Modes */}
      <section className="px-6 py-16 bg-[#F8FAFC]">
        <h2 className="text-3xl font-bold text-center text-[#0F172A] mb-12">Built for Every Stage</h2>
        <div className="flex flex-col md:flex-row gap-6 max-w-4xl mx-auto">
          {[
            { mode: 'Explorer', age: 'Under 13', desc: 'Fun, simple guidance for young curious minds.', color: '#14B8A6' },
            { mode: 'Discovery', age: 'Ages 13 to 17', desc: 'Helps secondary school students find their direction.', color: '#2563EB' },
            { mode: 'Career', age: '18 and above', desc: 'Deep career guidance for students and professionals.', color: '#F59E0B' },
          ].map((item) => (
            <div key={item.mode} className="flex-1 p-6 rounded-2xl border-2 shadow-sm" style={{ borderColor: item.color }}>
              <h3 className="text-xl font-bold mb-1" style={{ color: item.color }}>{item.mode} Mode</h3>
              <p className="text-sm text-[#64748B] mb-3">{item.age}</p>
              <p className="text-[#0F172A]">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-6 text-sm text-[#94A3B8]">
        Powered by Moses iluyemi 
      </footer>

    </div>
  )
}

export default Landing