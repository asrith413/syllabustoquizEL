import axios from 'axios'

export const API_BASE_URL =
  typeof window !== 'undefined'
    ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
    : 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

export const signup = async (userData: any) => {
  const response = await api.post('/auth/signup', userData)
  return response.data
}

export const login = async (credentials: any) => {
  const response = await api.post('/auth/login', credentials)
  return response.data
}

export const getHistory = async () => {
  const response = await api.get('/api/history')
  return response.data
}

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

export const generateQuiz = async (sessionId: string, numQuestions: number = 10) => {
  const response = await api.post('/api/generate-quiz', {
    session_id: sessionId,
    num_questions: numQuestions,
  })
  return response.data
}

export const generateAdaptiveQuiz = async (sessionId: string, numQuestions: number = 10) => {
  const response = await api.post('/api/generate-adaptive-quiz', {
    session_id: sessionId,
    num_questions: numQuestions,
  })
  return response.data
}

export const submitQuiz = async (
  quizId: string,
  sessionId: string,
  answers: Record<string, number>,
  time_taken?: Record<number, number>
) => {
  const response = await api.post('/api/submit-quiz', {
    quiz_id: quizId,
    session_id: sessionId,
    answers,
    time_taken
  })
  return response.data
}

export const getStats = async (sessionId: string) => {
  const response = await api.get(`/api/stats/${sessionId}`)
  return response.data
}
