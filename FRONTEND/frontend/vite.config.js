import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000,
  },
  build: {
    outDir: 'dist',
  },
  // Always use production API URL - do not allow override
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify('https://quick-health-hospital-appoitment-system-1.onrender.com')
  }
})
