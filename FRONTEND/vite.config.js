import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
  build: {
    outDir: 'dist',
  },
  // Explicitly set the backend URL for production
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify('https://quick-health-hospital-appoitment-system-1.onrender.com')
  }
})
