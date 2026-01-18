import axios from 'axios'

export const API_BASE_URL = 
  typeof window !== 'undefined' 
    ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
    : 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadImage = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const getTopics = async (sessionId: string) => {
  const response = await api.get(`/api/topics/${sessionId}`)
  return response.data
}

export const generateQuiz = async (sessionId: string, numQuestions: number = 18) => {
  const response = await api.post('/api/generate-quiz', {
    session_id: sessionId,
    num_questions: numQuestions,
  })
  return response.data
}

export const generateAdaptiveQuiz = async (sessionId: string, numQuestions: number = 18) => {
  const response = await api.post('/api/generate-adaptive-quiz', {
    session_id: sessionId,
    num_questions: numQuestions,
  })
  return response.data
}

export const submitQuiz = async (quizId: string, sessionId: string, answers: Record<string, number>) => {
  const response = await api.post('/api/submit-quiz', {
    quiz_id: quizId,
    session_id: sessionId,
    answers,
  })
  return response.data
}

export const getStats = async (sessionId: string) => {
  const response = await api.get(`/api/stats/${sessionId}`)
  return response.data
}
