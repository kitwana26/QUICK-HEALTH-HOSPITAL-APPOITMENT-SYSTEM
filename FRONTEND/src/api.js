import axios from 'axios'

// Explicitly set the production backend URL
const API_BASE_URL = 'https://quick-health-hospital-appoitment-system-1.onrender.com'

console.log('API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

// Add response interceptor for debugging
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.message)
    if (error.response) {
      console.error('Response status:', error.response.status)
      console.error('Response data:', error.response.data)
    } else if (error.code === 'ECONNABORTED') {
      console.error('Request timeout: backend may be waking up (cold start)')
    }
    return Promise.reject(error)
  }
)

export default api
