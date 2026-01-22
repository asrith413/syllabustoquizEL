import Link from 'next/link'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="flex justify-between items-center px-8 py-6 max-w-7xl mx-auto">
        <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
          SocratAI
        </div>
        <div className="space-x-4">
          <Link
            href="/auth/login"
            className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            Login
          </Link>
          <Link
            href="/auth/signup"
            className="bg-blue-600 text-white px-5 py-2.5 rounded-full font-medium hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
          >
            Sign Up
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center text-center mt-20 px-4">
        <h1 className="text-5xl md:text-7xl font-extrabold text-gray-900 tracking-tight mb-8 max-w-4xl">
          Master any syllabus with <span className="text-blue-600">SocratAI</span>
        </h1>
        <p className="text-xl text-gray-500 max-w-2xl mb-12 leading-relaxed">
          Upload your syllabus or notes, and let our AI generate adaptive quizzes to help you learn faster and retain more.
        </p>

        <Link
          href="/auth/signup"
          className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white transition-all duration-200 bg-blue-600 font-pj rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 hover:bg-blue-700 shadow-xl hover:translate-y-[-2px]"
        >
          Get Started for Free
          <svg className="w-5 h-5 ml-2 -mr-1 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
          </svg>
        </Link>
      </div>

      {/* Features Preview (Minimal) */}
      <div className="mt-32 max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-8 mb-20">
        {[
          { title: "Upload Notes", desc: "Simply snap a photo or upload a PDF of your syllabus." },
          { title: "Adaptive Quizzes", desc: "Questions that adapt to your skill level in real-time." },
          { title: "Track Progress", desc: "Visual analytics to identify your strengths and weaknesses." }
        ].map((feature, i) => (
          <div key={i} className="p-8 rounded-2xl bg-blue-50/50 border border-blue-100 hover:border-blue-200 transition-colors">
            <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
            <p className="text-gray-600">{feature.desc}</p>
          </div>
        ))}
      </div>
    </main>
  )
}
