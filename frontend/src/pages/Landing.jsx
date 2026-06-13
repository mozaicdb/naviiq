import { useNavigate } from 'react-router-dom'

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
        Powered by Alibaba Cloud and Qwen3.7-Plus · Optimized for low data
      </footer>

    </div>
  )
}

export default Landing