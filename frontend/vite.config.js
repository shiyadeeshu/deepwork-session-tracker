import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Port 3000 matches runapplication.bat and the backend CORS settings.
export default defineConfig({
  plugins: [react()],
  server: { port: 3000 },
  preview: { port: 3000 },
})
