import axios from 'axios'

// Use environment variable or default to production URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://quick-health-hospital-appoitment-system-1.onrender.com'

console.log('API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
})

export default api
