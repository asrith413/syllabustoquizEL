'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import ImageUpload from '@/components/ImageUpload'
import QuizModule from '@/components/QuizModule'
import StatsDashboard from '@/components/StatsDashboard'
import { useAuth } from '@/context/AuthContext'
import { getHistory } from '@/lib/api'

export default function Dashboard() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [topics, setTopics] = useState<string[]>([])
  const [currentView, setCurrentView] = useState<'upload' | 'warmup' | 'quiz' | 'stats' | 'history'>('upload')
  const [quizType, setQuizType] = useState<'initial' | 'adaptive'>('initial')
  const [lastScore, setLastScore] = useState<number | null>(null)
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [history, setHistory] = useState<any[]>([])

  const { user, logout, isLoading, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isLoading, isAuthenticated, router])

  const handleUploadSuccess = (sessionId: string, topics: string[], previewUrl: string | null) => {
    setSessionId(sessionId)
    setTopics(topics)
    setPreviewImage(previewUrl)
    setCurrentView('warmup')
  }

  const handleStartQuiz = (type: 'initial' | 'adaptive') => {
    setQuizType(type)
    setCurrentView('quiz')
  }

  const handleQuizComplete = (score: number) => {
    setLastScore(score)
    setCurrentView('stats')
  }

  const handleViewStats = () => {
    setCurrentView('stats')
  }

  const loadHistory = async () => {
    try {
      const data = await getHistory()
      setHistory(data)
      setCurrentView('history')
    } catch (error) {
      console.error("Failed to load history", error)
    }
  }

  if (isLoading || !isAuthenticated) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setCurrentView('upload')}
                className="text-2xl font-bold text-indigo-600 hover:text-indigo-800 transition-colors"
              >
                SocratAI
              </button>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.username}</span>
              <button
                onClick={() => setCurrentView('upload')}
                className="text-gray-600 hover:text-indigo-600 font-medium"
              >
                New Upload
              </button>
              <button
                onClick={loadHistory}
                className="text-gray-600 hover:text-indigo-600 font-medium"
              >
                History
              </button>
              <button
                onClick={logout}
                className="text-red-600 hover:text-red-700 font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="bg-white rounded-lg shadow-lg p-6">
          {currentView === 'history' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-800">Your Quiz History</h2>
              {history.length === 0 ? (
                <p className="text-gray-500">No history found. Start a new quiz!</p>
              ) : (
                <div className="grid gap-4">
                  {history.map((session: any) => (
                    <div key={session.session_id} className="border p-4 rounded-lg hover:shadow-md transition-shadow bg-white flex flex-col md:flex-row gap-4">
                      {/* Image Thumbnail */}
                      <div className="w-full md:w-32 h-32 bg-gray-100 rounded-md overflow-hidden flex-shrink-0">
                        {session.image_path ? (
                          <img
                            src={`http://localhost:8000/${session.image_path}`}
                            alt="Session"
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-gray-400 text-xs">No Image</div>
                        )}
                      </div>

                      <div className="flex-1 flex flex-col justify-between">
                        <div>
                          <div className="flex justify-between items-start">
                            <h3 className="font-semibold text-lg text-gray-800">
                              {new Date(session.created_at).toLocaleDateString()}
                            </h3>
                            {session.last_score !== null && (
                              <span className={`px-2 py-1 rounded text-xs font-bold ${session.last_score >= 80 ? 'bg-green-100 text-green-700' :
                                  session.last_score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                                    'bg-red-100 text-red-700'
                                }`}>
                                Last Score: {session.last_score.toFixed(0)}%
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                            {session.topics.join(", ")}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {session.topics.length} topics identified
                          </p>
                        </div>

                        <div className="mt-4 flex gap-2">
                          <button
                            onClick={() => {
                              setSessionId(session.session_id)
                              setTopics(session.topics)
                              // If image exists, set it for preview too?
                              if (session.image_path) setPreviewImage(`http://localhost:8000/${session.image_path}`)
                              setCurrentView('stats')
                            }}
                            className="text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded text-sm font-medium transition-colors"
                          >
                            View Stats
                          </button>
                          <button
                            onClick={() => {
                              setSessionId(session.session_id)
                              setTopics(session.topics)
                              if (session.image_path) setPreviewImage(`http://localhost:8000/${session.image_path}`)
                              setCurrentView('warmup')
                            }}
                            className="text-indigo-600 border border-indigo-600 hover:bg-indigo-50 px-4 py-2 rounded text-sm font-medium transition-colors"
                          >
                            Take Quiz
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {currentView === 'upload' && (
            <div className="space-y-8">
              <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl p-8 text-white shadow-lg mb-8">
                <h1 className="text-3xl font-bold mb-2">Hello, {user?.username}! 👋</h1>
                <p className="opacity-90">Ready to turn your syllabus into a mastery plan? Upload below to get started.</p>
              </div>
              <ImageUpload onSuccess={handleUploadSuccess} />
            </div>
          )}

          {currentView === 'warmup' && sessionId && (
            <div className="text-center space-y-6 py-8">
              <h2 className="text-2xl font-semibold text-gray-800">
                Ready to Generate Quiz
              </h2>

              {previewImage && (
                <div className="relative max-w-md mx-auto aspect-video rounded-lg overflow-hidden shadow-md bg-gray-100">
                  <img
                    src={previewImage}
                    alt="Syllabus Preview"
                    className="w-full h-full object-contain"
                  />
                </div>
              )}

              {!previewImage && (
                <div className="p-8 bg-gray-100 rounded-lg text-gray-500">
                  No preview available for this session
                </div>
              )}

              <div className="flex gap-4 justify-center max-w-md mx-auto">
                <button
                  onClick={() => handleStartQuiz('initial')}
                  className="flex-1 bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 transition-colors shadow-sm"
                >
                  Start Quiz
                </button>
                <button
                  onClick={() => setCurrentView('upload')}
                  className="px-6 py-3 text-gray-600 hover:text-gray-800 font-medium hover:bg-gray-50 rounded-lg transition-colors border border-transparent hover:border-gray-200"
                >
                  Start Over
                </button>
              </div>
            </div>
          )}

          {currentView === 'quiz' && sessionId && (
            <QuizModule
              sessionId={sessionId}
              quizType={quizType}
              onComplete={handleQuizComplete}
              onBack={() => setCurrentView('warmup')}
            />
          )}

          {currentView === 'stats' && sessionId && (
            <StatsDashboard
              sessionId={sessionId}
              onBack={() => setCurrentView('warmup')}
              onStartAdaptiveQuiz={() => handleStartQuiz('adaptive')}
            />
          )}
        </div>
      </div>
    </main>
  )
}
