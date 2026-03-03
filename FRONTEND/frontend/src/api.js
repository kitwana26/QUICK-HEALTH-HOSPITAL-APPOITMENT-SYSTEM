import axios from 'axios'

// Hardcoded production API URL - do not change
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
      if (error.response.status === 401) {
        const detail = error.response.data?.detail || ''
        const errMsg = String(detail).toLowerCase()
        if (errMsg.includes('invalid token') || errMsg.includes('authentication credentials')) {
          localStorage.removeItem('token')
          localStorage.removeItem('role')
          localStorage.removeItem('username')
          localStorage.removeItem('name')
          if (typeof window !== 'undefined') {
            window.alert('Session imeisha. Tafadhali login tena.')
            window.location.reload()
          }
        }
      }
    } else if (error.code === 'ECONNABORTED') {
      console.error('Request timeout: backend may be waking up (cold start)')
    }
    return Promise.reject(error)
  }
)

export default api
