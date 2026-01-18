'use client'

import { useState } from 'react'
import ImageUpload from '@/components/ImageUpload'
import TopicsList from '@/components/TopicsList'
import QuizModule from '@/components/QuizModule'
import StatsDashboard from '@/components/StatsDashboard'
import { API_BASE_URL } from '@/lib/api'

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [topics, setTopics] = useState<string[]>([])
  const [currentView, setCurrentView] = useState<'upload' | 'topics' | 'quiz' | 'stats'>('upload')
  const [quizType, setQuizType] = useState<'initial' | 'adaptive'>('initial')
  const [lastScore, setLastScore] = useState<number | null>(null)

  const handleUploadSuccess = (sessionId: string, topics: string[]) => {
    setSessionId(sessionId)
    setTopics(topics)
    setCurrentView('topics')
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

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Syllabus to Quiz
          </h1>
          <p className="text-gray-600">
            Transform your syllabus into adaptive learning quizzes
          </p>
        </header>

        <div className="bg-white rounded-lg shadow-lg p-6">
          {currentView === 'upload' && (
            <ImageUpload onSuccess={handleUploadSuccess} />
          )}

          {currentView === 'topics' && sessionId && (
            <div>
              <TopicsList 
                sessionId={sessionId} 
                topics={topics}
                onStartQuiz={handleStartQuiz}
                onViewStats={handleViewStats}
              />
            </div>
          )}

          {currentView === 'quiz' && sessionId && (
            <QuizModule
              sessionId={sessionId}
              quizType={quizType}
              onComplete={handleQuizComplete}
              onBack={() => setCurrentView('topics')}
            />
          )}

          {currentView === 'stats' && sessionId && (
            <StatsDashboard
              sessionId={sessionId}
              onBack={() => setCurrentView('topics')}
              onStartAdaptiveQuiz={() => handleStartQuiz('adaptive')}
            />
          )}
        </div>
      </div>
    </main>
  )
}
