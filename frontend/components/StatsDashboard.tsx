'use client'

import { useState, useEffect } from 'react'
import { getStats } from '@/lib/api'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  AreaChart,
  Area,
} from 'recharts'

interface StatsDashboardProps {
  sessionId: string
  onBack: () => void
  onStartAdaptiveQuiz: () => void
}

export default function StatsDashboard({ sessionId, onBack, onStartAdaptiveQuiz }: StatsDashboardProps) {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
  }, [sessionId])

  const loadStats = async () => {
    setLoading(true)
    try {
      const data = await getStats(sessionId)
      setStats(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load stats')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p className="mt-4 text-gray-600">Loading statistics...</p>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="text-center py-12">
        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded mb-4">
          {error === 'No stats found' ? 'You haven\'t taken any quizzes for this session yet.' : (error || 'No statistics available')}
        </div>

        {error === 'No stats found' ? (
          <button
            onClick={onStartAdaptiveQuiz} // Re-using this to start initial quiz would be better, but adaptive works as "Start"
            className="bg-primary-600 text-white py-2 px-6 rounded-lg font-semibold hover:bg-primary-700 transition-colors mr-3"
          >
            Take a Quiz
          </button>
        ) : null}

        <button
          onClick={onBack}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          Go Back
        </button>
      </div>
    )
  }

  const quizHistoryData = stats.quiz_history.map((quiz: any) => ({
    name: `Quiz ${quiz.quiz_number}`,
    score: quiz.score,
  }))

  const topicData = stats.bloom_performance
    ? Object.entries(stats.bloom_performance).map(([level, score]) => ({
      subject: level,
      A: score as number,
      fullMark: 100,
    }))
    : Object.entries(stats.topic_performance).map(([topic, score]) => ({
      subject: topic.length > 20 ? topic.substring(0, 20) + '...' : topic,
      A: score as number,
      fullMark: 100,
    }))

  const timeData = stats.bloom_time_performance
    ? Object.entries(stats.bloom_time_performance).map(([level, time]) => ({
      name: level,
      seconds: time as number,
    }))
    : []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-800">
          Performance Statistics
        </h2>
        <button
          onClick={onBack}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-6">
          <div className="text-sm text-blue-600 font-medium mb-1">
            Total Quizzes
          </div>
          <div className="text-3xl font-bold text-blue-700">
            {stats.total_quizzes}
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-6">
          <div className="text-sm text-green-600 font-medium mb-1">
            Average Score
          </div>
          <div className="text-3xl font-bold text-green-700">
            {stats.average_score.toFixed(1)}%
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-6">
          <div className="text-sm text-purple-600 font-medium mb-1">
            Topics Covered
          </div>
          <div className="text-3xl font-bold text-purple-700">
            {Object.keys(stats.topic_performance).length}
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Quiz Performance Over Time
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={quizHistoryData}>
            <defs>
              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Area
              type="monotone"
              dataKey="score"
              stroke="#8884d8"
              fillOpacity={1}
              fill="url(#colorScore)"
              name="Score (%)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Cognitive Proficiency (Bloom's Taxonomy)
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={topicData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <PolarRadiusAxis domain={[0, 100]} />
            <Radar
              name="Score"
              dataKey="A"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.6}
            />
            <Tooltip />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Average Time per Cognitive Level (Seconds)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={timeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value: number) => [`${value.toFixed(1)}s`, 'Avg Time']} />
            <Legend />
            <Bar dataKey="seconds" name="Avg Time (s)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="flex gap-4">
        <button
          onClick={onStartAdaptiveQuiz}
          className="flex-1 bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
        >
          Take Adaptive Quiz
        </button>
        <button
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          Back to Topics
        </button>
      </div>
    </div >
  )
}
