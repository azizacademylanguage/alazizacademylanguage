import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false, // agar 5173 band bo'lsa, keyingi bo'sh portga o'tadi (masalan 5174)
  },
})
