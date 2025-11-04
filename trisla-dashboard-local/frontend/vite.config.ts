import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Porta padrão 5173
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
  },
})
