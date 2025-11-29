import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      'localhost',
      'aurora.siyahkare.com',
      '.siyahkare.com',
    ],
    proxy: {
      // Proxy /v1/* requests to backend
      '/v1': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})
