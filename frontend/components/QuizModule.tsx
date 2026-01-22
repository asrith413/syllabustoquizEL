'use client'

import { useState, useEffect, useRef } from 'react'
import { generateQuiz, generateAdaptiveQuiz, submitQuiz } from '@/lib/api'

interface QuizModuleProps {
  sessionId: string
  quizType: 'initial' | 'adaptive'
  onComplete: (score: number) => void
  onBack: () => void
}

interface Question {
  question: string
  options: string[]
  correct_answer: number
  bloom_level?: string
}

interface TimeTracking {
  [key: number]: number // questionIndex -> seconds
}

export default function QuizModule({ sessionId, quizType, onComplete, onBack }: QuizModuleProps) {
  // ... (unchanged)


  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [quizId, setQuizId] = useState<string | null>(null)
  const [results, setResults] = useState<any>(null)
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null)

  // Time tracking state
  const [timeSpent, setTimeSpent] = useState<TimeTracking>({})
  const startTimeRef = useRef<number>(Date.now())

  // Update time when changing questions or submitting
  const updateTime = () => {
    const now = Date.now()
    const elapsed = (now - startTimeRef.current) / 1000
    setTimeSpent(prev => ({
      ...prev,
      [currentQuestion]: (prev[currentQuestion] || 0) + elapsed
    }))
    startTimeRef.current = now // Reset start time for next segment/question
  }

  // Effect to handle visibility change (tab switching) to maintain accuracy? 
  // For now, simple start/stop on question change is enough.


  const initialized = useRef(false)

  const toggleExpand = (idx: number) => {
    if (expandedQuestion === idx) {
      setExpandedQuestion(null)
    } else {
      setExpandedQuestion(idx)
    }
  }

  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true
      loadQuiz()
    }
  }, [sessionId, quizType])

  const loadQuiz = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = quizType === 'initial'
        ? await generateQuiz(sessionId)
        : await generateAdaptiveQuiz(sessionId)

      setQuestions(result.questions)
      setQuizId(result.quiz_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load quiz')
      initialized.current = false // Allow retry on error
    } finally {
      setLoading(false)
    }
  }

  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    setAnswers({
      ...answers,
      [questionIndex]: answerIndex,
    })
  }

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      updateTime()
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      updateTime()
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleSubmit = async () => {
    if (!quizId) return

    setSubmitting(true)
    updateTime() // tracking for the last question
    try {
      // Need to wait for state update? Actually updateTime returns void and sets async state.
      // Better to calculate final time directly here to avoid race condition.
      const now = Date.now()
      const elapsed = (now - startTimeRef.current) / 1000
      const finalTimeSpent = {
        ...timeSpent,
        [currentQuestion]: (timeSpent[currentQuestion] || 0) + elapsed
      }

      const result = await submitQuiz(quizId, sessionId, answers, finalTimeSpent)
      setResults(result)
      setResults(result)
      // Removed auto-redirect
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit quiz')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p className="mt-4 text-gray-600">Generating quiz questions...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
        <button
          onClick={onBack}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          Go Back
        </button>
      </div>
    )
  }



  if (results) {
    return (
      <div className="text-center py-12 max-w-2xl mx-auto">
        <div className="mb-6">
          <div className="text-6xl font-bold text-primary-600 mb-2">
            {results.score.toFixed(1)}%
          </div>
          <p className="text-xl text-gray-700">
            You scored {results.correct} out of {results.total}
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left shadow-inner">
          <h3 className="font-semibold text-gray-800 mb-4 text-lg">Detailed Results</h3>
          <p className="text-sm text-gray-500 mb-4">Click on a question to see details</p>
          <div className="space-y-3">
            {results.results.map((result: any, idx: number) => (
              <div
                key={idx}
                className={`border rounded-lg overflow-hidden transition-all duration-200 ${expandedQuestion === idx ? 'bg-white shadow-md' : 'bg-white'
                  }`}
              >
                <div
                  onClick={() => toggleExpand(idx)}
                  className={`p-4 cursor-pointer flex items-center justify-between hover:bg-gray-50 ${result.is_correct ? 'border-l-4 border-l-green-500' : 'border-l-4 border-l-red-500'
                    }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${result.is_correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                      {idx + 1}
                    </span>
                    <span className="font-medium text-gray-700">Question {idx + 1}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-semibold ${result.is_correct ? 'text-green-600' : 'text-red-600'}`}>
                      {result.is_correct ? 'Correct' : 'Incorrect'}
                    </span>
                    <span className="text-gray-400 text-sm">{expandedQuestion === idx ? '▲' : '▼'}</span>
                  </div>
                </div>

                {expandedQuestion === idx && (
                  <div className="p-4 border-t bg-gray-50 text-left">
                    <div className="flex justify-between items-start mb-3">
                      <p className="font-medium text-gray-800 flex-1">{questions[idx].question}</p>
                      {result.time_taken !== undefined && (
                        <span className="text-xs font-mono bg-blue-100 text-blue-800 px-2 py-1 rounded ml-2 whitespace-nowrap">
                          ⏱ {result.time_taken.toFixed(1)}s
                        </span>
                      )}
                    </div>

                    <div className="space-y-2">
                      <div className="text-sm">
                        <span className="font-semibold text-gray-500">Your Answer:</span>
                        <div className={`mt-1 p-2 rounded border ${result.is_correct
                          ? 'bg-green-50 border-green-200 text-green-800'
                          : 'bg-red-50 border-red-200 text-red-800'
                          }`}>
                          {questions[idx].options[result.user_answer]}
                        </div>
                      </div>

                      {!result.is_correct && (
                        <div className="text-sm mt-3">
                          <span className="font-semibold text-gray-500">Correct Answer:</span>
                          <div className="mt-1 p-2 rounded border bg-green-50 border-green-200 text-green-800">
                            {questions[idx].options[result.correct_answer]}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <p className="text-gray-600 mb-6">
          Next quiz difficulty: <span className="font-semibold capitalize text-primary-600">{results.next_difficulty}</span>
        </p>

        <button
          onClick={() => onComplete(results.score)}
          className="bg-primary-600 text-white py-3 px-8 rounded-full font-bold text-lg hover:bg-primary-700 transition-transform transform hover:scale-105 shadow-lg"
        >
          Continue to Stats →
        </button>
      </div>
    )
  }

  const question = questions[currentQuestion]
  const progress = ((currentQuestion + 1) / questions.length) * 100
  const answeredCount = Object.keys(answers).length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <button
          onClick={onBack}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back
        </button>
        <div className="text-sm text-gray-600">
          Question {currentQuestion + 1} of {questions.length}
        </div>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-primary-600 h-2 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex justify-between items-start mb-6 gap-4">
          <h3 className="text-xl font-semibold text-gray-800">
            {question.question}
          </h3>
          {question.bloom_level && (
            <span className="shrink-0 px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-full uppercase tracking-wide">
              {question.bloom_level}
            </span>
          )}
        </div>

        <div className="space-y-3">
          {question.options.map((option, index) => (
            <label
              key={index}
              className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${answers[currentQuestion] === index
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
                }`}
            >
              <input
                type="radio"
                name={`question-${currentQuestion}`}
                value={index}
                checked={answers[currentQuestion] === index}
                onChange={() => handleAnswerSelect(currentQuestion, index)}
                className="mr-3 w-4 h-4 text-primary-600"
              />
              <span className="text-gray-800">{option}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex justify-between">
        <button
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          Previous
        </button>

        {currentQuestion < questions.length - 1 ? (
          <button
            onClick={handleNext}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={submitting || answeredCount < questions.length}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Submitting...' : 'Submit Quiz'}
          </button>
        )}
      </div>

      <div className="text-center text-sm text-gray-500">
        {answeredCount} of {questions.length} questions answered
      </div>
    </div>
  )
}
