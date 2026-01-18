'use client'

import { useState, useEffect } from 'react'
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
}

export default function QuizModule({ sessionId, quizType, onComplete, onBack }: QuizModuleProps) {
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [quizId, setQuizId] = useState<string | null>(null)
  const [results, setResults] = useState<any>(null)

  useEffect(() => {
    loadQuiz()
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
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleSubmit = async () => {
    if (!quizId) return
    
    setSubmitting(true)
    try {
      const result = await submitQuiz(quizId, sessionId, answers)
      setResults(result)
      setTimeout(() => {
        onComplete(result.score)
      }, 3000)
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
      <div className="text-center py-12">
        <div className="mb-6">
          <div className="text-6xl font-bold text-primary-600 mb-2">
            {results.score.toFixed(1)}%
          </div>
          <p className="text-xl text-gray-700">
            You scored {results.correct} out of {results.total}
          </p>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
          <h3 className="font-semibold text-gray-800 mb-4">Results Summary</h3>
          <div className="space-y-2">
            {results.results.map((result: any, idx: number) => (
              <div
                key={idx}
                className={`p-3 rounded ${
                  result.is_correct ? 'bg-green-50' : 'bg-red-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm">Question {idx + 1}</span>
                  <span className={`font-medium ${
                    result.is_correct ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {result.is_correct ? '✓ Correct' : '✗ Incorrect'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-gray-600 mb-4">
          Next quiz difficulty: <span className="font-semibold capitalize">{results.next_difficulty}</span>
        </p>
        
        <p className="text-sm text-gray-500">Redirecting to stats...</p>
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
        <h3 className="text-xl font-semibold text-gray-800 mb-6">
          {question.question}
        </h3>

        <div className="space-y-3">
          {question.options.map((option, index) => (
            <label
              key={index}
              className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                answers[currentQuestion] === index
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
